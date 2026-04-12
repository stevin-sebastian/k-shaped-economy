import numpy as np
import pandas as pd
from data import config as data_config


def rebase_series(df, base_date_str):
    """
    Rebase all columns in df so that each equals 100 at base_date_str.
    Uses the nearest available date when an exact match is absent.
    """
    try:
        base_date = pd.to_datetime(base_date_str)
        idx_loc = df.index.get_indexer([base_date], method="nearest")[0]
        base_vals = df.iloc[idx_loc].replace(0, np.nan)
        return df.div(base_vals) * 100
    except Exception as e:
        print(f"Error rebasing data: {e}")
        return df.copy()


def align_to_monthly(df):
    """
    Normalise mixed-frequency data to month-end.
    Daily series: take the last observation of the month.
    Quarterly/annual series: forward-fill into each month.
    """
    try:
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        monthly = df.resample("ME").last().ffill()
        return monthly
    except Exception as e:
        print(f"Error aligning to monthly: {e}")
        return df.copy()


def compute_real_wages_and_cpi(df):
    """
    Adds REAL_WAGE_LOW_WAGE_RAW = nominal wage / CPI * 100.
    Works on the raw (pre-rebase) DataFrame.
    """
    out = df.copy()
    if "WAGE_LOW_WAGE" in out.columns and "CPIAUCSL" in out.columns:
        out["REAL_WAGE_LOW_WAGE_RAW"] = (out["WAGE_LOW_WAGE"] / out["CPIAUCSL"]) * 100
    return out


def compute_normalized_real_wage(rebased_df, raw_df):
    """
    Rebases REAL_WAGE_LOW_WAGE_RAW to START_DATE = 100 and stores it
    as REAL_WAGE_LOW_WAGE in the rebased DataFrame.
    """
    out = rebased_df.copy()
    try:
        if "REAL_WAGE_LOW_WAGE_RAW" in raw_df.columns:
            tmp = raw_df[["REAL_WAGE_LOW_WAGE_RAW"]].rename(
                columns={"REAL_WAGE_LOW_WAGE_RAW": "REAL_WAGE_LOW_WAGE"}
            )
            tmp_rebased = rebase_series(tmp, data_config.START_DATE)
            out["REAL_WAGE_LOW_WAGE"] = tmp_rebased["REAL_WAGE_LOW_WAGE"]
    except Exception:
        pass
    return out


def calculate_k_indices(df_normalized):
    """
    Computes the two composite K-shaped indices (both indexed to Jan 2020 = 100).

    Upper Arm (K_UPPER) — asset-holder economy:
        Average of:
          1. S&P 500 index (equities)
          2. Case-Shiller national home price index (real estate)
        Both indexed to Jan 2020 = 100.  Together they represent the two dominant
        asset classes of wealthier households.

    Lower Arm (K_LOWER) — working-class economy:
        Average of:
          1. Leisure & Hospitality employment index
          2. Real production-worker hourly earnings index
             (nominal wages / CPI — uses production/nonsupervisory workers
              to avoid the COVID composition-bias in sector-specific wages)
          3. Inverted average delinquency index
             (higher delinquency → lower index value)
          4. Bottom 50% wealth share index
        All indexed to Jan 2020 = 100.
    """
    out = df_normalized.copy()
    baseline = pd.to_datetime("2020-01-01")

    def index_series(raw_name, fallback_name=None):
        """Index a series to 100 at baseline; fall back to normalised column."""
        for name in [raw_name, fallback_name]:
            if name and name in out.columns:
                s = out[name].astype(float)
                try:
                    loc = out.index.get_indexer([baseline], method="nearest")[0]
                    base = float(s.iloc[loc])
                    if base == 0 or np.isnan(base):
                        continue
                    return (s / base) * 100
                except Exception:
                    continue
        return pd.Series(np.nan, index=out.index)

    # ── Upper Arm ──────────────────────────────────────────────────────────────
    sp500_idx      = index_series("SP500_RAW",       "SP500")
    home_price_idx = index_series("HOME_PRICES_RAW", "HOME_PRICES")
    out["K_UPPER"] = (sp500_idx + home_price_idx) / 2

    # ── Lower Arm ──────────────────────────────────────────────────────────────
    emp_idx          = index_series("EMP_LOW_WAGE_RAW",      "EMP_LOW_WAGE")
    bottom_wealth_idx = index_series("WEALTH_BOTTOM50_RAW",  "WEALTH_BOTTOM50")

    # Prefer CPI-deflated real wages; fall back to nominal
    wage_idx = index_series("REAL_WAGE_LOW_WAGE_RAW", "REAL_WAGE_LOW_WAGE")
    if wage_idx.isna().all():
        wage_idx = index_series("WAGE_LOW_WAGE_RAW", "WAGE_LOW_WAGE")

    # Delinquency: average of available series, then invert
    delinq_cols = [k for k in ["DRCCLACBS_RAW", "DRCLACBS_RAW"] if k in out.columns]
    if delinq_cols:
        avg_delinq = pd.concat([out[k].astype(float) for k in delinq_cols], axis=1).mean(axis=1)
        try:
            loc = out.index.get_indexer([baseline], method="nearest")[0]
            base_d = float(avg_delinq.iloc[loc])
            # Invert: higher delinquency → lower index value
            inverted = 100 - ((avg_delinq - base_d) / base_d * 100)
        except Exception:
            inverted = pd.Series(100.0, index=out.index)
    else:
        inverted = pd.Series(100.0, index=out.index)

    out["K_LOWER"] = (emp_idx + wage_idx + inverted + bottom_wealth_idx) / 4

    return out
