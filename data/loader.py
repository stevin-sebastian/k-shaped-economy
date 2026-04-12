import datetime
import functools
import pandas as pd
from . import config


def load_fred_series(series_id, series_name):
    """
    Fetches a single series from FRED via direct CSV URL.
    Returns a DataFrame with DatetimeIndex and one column named series_name.
    """
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    try:
        df = pd.read_csv(url, parse_dates=[0], index_col=0)
        if series_id in df.columns:
            df = df.rename(columns={series_id: series_name})
        else:
            df.columns = [series_name]
        if config.START_DATE:
            df = df[df.index >= pd.to_datetime(config.START_DATE)]
        df[series_name] = pd.to_numeric(df[series_name], errors="coerce")
        return df
    except Exception as e:
        print(f"FAILED to load {series_name} ({series_id}): {e}")
        return pd.DataFrame()


@functools.lru_cache(maxsize=7)
def _fetch_all_data(date_key: datetime.date) -> pd.DataFrame:
    """
    Internal cached fetch keyed by calendar date so data refreshes
    automatically each day the server is running.
    """
    merged = pd.DataFrame()
    for internal_id, fred_id in config.SERIES_IDS.items():
        df = load_fred_series(fred_id, internal_id)
        if merged.empty:
            merged = df
        else:
            merged = merged.join(df, how="outer")

    merged = merged.sort_index().ffill()

    # Synthesise illustrative tariff series from config schedule
    try:
        tariff = pd.Series(index=merged.index, dtype=float)
        for date_str, val in config.TARIFF_SCHEDULE:
            tariff.loc[tariff.index >= pd.to_datetime(date_str)] = val
        merged["TARIFF_RATE"] = tariff.ffill().fillna(0)
    except Exception as e:
        print(f"Failed to synthesise tariff series: {e}")

    return merged


def get_all_data() -> pd.DataFrame:
    """
    Returns the merged FRED DataFrame, refreshed once per calendar day.
    Calling this multiple times within the same day returns the cached copy.
    """
    return _fetch_all_data(datetime.date.today())
