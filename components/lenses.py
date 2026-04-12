import pandas as pd
import plotly.graph_objects as go
from data import config as data_config

COLORS = data_config.COLORS

# ── Shared dark theme template ─────────────────────────────────────────────────
DARK_TEMPLATE = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text_secondary"], family="Inter, sans-serif"),
    xaxis=dict(showgrid=False, zeroline=False, showline=True,
                linewidth=1, linecolor=COLORS["border_subtle"]),
    yaxis=dict(showgrid=True, gridwidth=1,
                gridcolor="rgba(255,255,255,0.05)", zeroline=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=20, t=30, b=40),
)

# ── Shared rangeselector (added to every chart's x-axis) ──────────────────────
def _rangeselector():
    return dict(
        bgcolor="rgba(20, 24, 36, 0.9)",
        activecolor="rgba(16, 185, 129, 0.25)",
        bordercolor="#2d3748",
        borderwidth=1,
        font=dict(color="#9aa0b1", size=10),
        buttons=[
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(count=3, label="3Y", step="year", stepmode="backward"),
            dict(step="all", label="All"),
        ],
    )


def _today():
    return pd.Timestamp.now().strftime("%Y-%m-%d")


# ── Lens 1: Labor Reality ──────────────────────────────────────────────────────
def create_labor_lens(df):
    fig = go.Figure()

    baseline = pd.to_datetime("2020-01-01")

    # Headline unemployment (left axis)
    unrate_key = "UNRATE_RAW" if "UNRATE_RAW" in df.columns else "UNRATE"
    if unrate_key in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df[unrate_key],
            name="Unemployment Rate",
            line=dict(color="#6366f1", width=2.5),
            hovertemplate="%{y:.1f}%",
        ))

    def _index_to_baseline(key):
        s = df[key].astype(float).ffill().bfill()
        base = float(s.asof(baseline)) if s.asof(baseline) is not None else float(s.iloc[0])
        return (s / base) * 100.0

    # Total nonfarm employment (right axis, indexed)
    payems_key = "PAYEMS_RAW" if "PAYEMS_RAW" in df.columns else "PAYEMS"
    if payems_key in df.columns:
        try:
            idx = _index_to_baseline(payems_key)
            fig.add_trace(go.Scatter(
                x=idx.index, y=idx.values,
                name="Total Nonfarm Employment",
                line=dict(color="#10b981", width=2, dash="dot"),
                yaxis="y2",
                hovertemplate="%{y:.1f}",
            ))
        except Exception:
            pass

    # L&H employment (right axis, indexed) — low-wage sector proxy
    lh_key = "EMP_LOW_WAGE_RAW" if "EMP_LOW_WAGE_RAW" in df.columns else "EMP_LOW_WAGE"
    if lh_key in df.columns:
        try:
            idx = _index_to_baseline(lh_key)
            fig.add_trace(go.Scatter(
                x=idx.index, y=idx.values,
                name="Leisure & Hospitality Employment",
                line=dict(color="#ef4444", width=3),
                yaxis="y2",
                hovertemplate="%{y:.1f}",
            ))
        except Exception:
            pass

    # COVID collapse annotation
    fig.add_annotation(
        x="2020-04-01", y=78,
        xref="x", yref="y2",
        text="<b>COVID collapse</b><br><span style='font-size:8px'>L&H lost 49% of jobs</span>",
        showarrow=True, arrowhead=2,
        arrowcolor="#ef4444", arrowwidth=1.5,
        ax=50, ay=-30,
        font=dict(size=9, color=COLORS["text_primary"]),
        bgcolor="rgba(30, 36, 51, 0.85)",
        bordercolor="#ef4444", borderwidth=1.5, borderpad=3,
    )

    # Recovery lag annotation
    fig.add_annotation(
        x="2022-09-01", y=95,
        xref="x", yref="y2",
        text="L&H recovery<br>lagged total by 18+ mo.",
        showarrow=True, arrowhead=2,
        arrowcolor="#ef4444", arrowwidth=1.2,
        ax=-40, ay=25,
        font=dict(size=9, color=COLORS["text_primary"]),
        bgcolor="rgba(30, 36, 51, 0.85)",
        bordercolor="#ef4444", borderwidth=1, borderpad=3,
    )

    # Baseline vline
    fig.add_vline(x=baseline, line_dash="dash",
                  line_color="rgba(255,255,255,0.15)", line_width=1.5)
    fig.add_annotation(
        x=baseline, y=14.5,
        text="Jan 2020", showarrow=False,
        font=dict(size=8, color=COLORS["text_secondary"]),
        bgcolor="rgba(30, 36, 51, 0.6)",
    )

    fig.update_layout(**{
        **DARK_TEMPLATE,
        "paper_bgcolor": COLORS["bg_secondary"],
        "plot_bgcolor":  COLORS["bg_secondary"],
        "font": dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
        "xaxis": dict(
            type="date", rangeselector=_rangeselector(),
            gridcolor="rgba(255,255,255,0.05)", color=COLORS["text_secondary"],
        ),
        "yaxis": dict(
            title=dict(text="<b>Unemployment Rate (%)</b>",
                       font=dict(color="#6366f1", size=11)),
            tickfont=dict(color="#6366f1"),
            range=[3, 16], showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
        ),
        "yaxis2": dict(
            overlaying="y", side="right", showgrid=False,
            title=dict(text="<b>Employment (Jan 2020 = 100)</b>",
                       font=dict(color="#10b981", size=11)),
            tickfont=dict(color=COLORS["text_secondary"]),
            range=[60, 110],
        ),
        "hovermode": "x unified",
        "legend": dict(
            orientation="h", yanchor="bottom", y=-0.40, xanchor="center", x=0.5,
            bgcolor="rgba(30, 36, 51, 0.85)", bordercolor="#4b5563",
            borderwidth=1, font=dict(size=10, color=COLORS["text_primary"]),
        ),
        "margin": dict(l=65, r=65, t=35, b=100),
    })
    return fig


# ── Lens 2: Policy vs. Affordability ──────────────────────────────────────────
def create_price_lens(df):
    fig = go.Figure()
    baseline = pd.to_datetime("2020-01-01")
    today = _today()

    def _index(series):
        base = series.asof(baseline)
        if base is None or pd.isna(base):
            base = series.iloc[0]
        return (series / float(base)) * 100.0

    # CPI
    cpi_key = "CPIAUCSL_RAW" if "CPIAUCSL_RAW" in df.columns else "CPIAUCSL"
    if cpi_key in df.columns:
        try:
            cpi_idx = _index(df[cpi_key].astype(float))
            fig.add_trace(go.Scatter(
                x=cpi_idx.index, y=cpi_idx.values,
                name="Consumer Prices (CPI)",
                line=dict(color="#f59e0b", width=3.5),
                hovertemplate="%{y:.1f}",
            ))
        except Exception:
            pass

    # Real production-worker wages
    wage_series = None
    for key in ["REAL_WAGE_LOW_WAGE_RAW", "REAL_WAGE_LOW_WAGE"]:
        if key in df.columns:
            wage_series = df[key].astype(float)
            break
    if wage_series is None:
        nom_key = "WAGE_LOW_WAGE_RAW" if "WAGE_LOW_WAGE_RAW" in df.columns else "WAGE_LOW_WAGE"
        cpi_raw = "CPIAUCSL_RAW" if "CPIAUCSL_RAW" in df.columns else "CPIAUCSL"
        if nom_key in df.columns and cpi_raw in df.columns:
            try:
                cpi_base = float(df[cpi_raw].astype(float).asof(baseline))
                wage_series = (df[nom_key].astype(float) * cpi_base) / df[cpi_raw].astype(float)
            except Exception:
                pass
    if wage_series is not None:
        try:
            wage_idx = _index(wage_series.dropna())
            fig.add_trace(go.Scatter(
                x=wage_idx.index, y=wage_idx.values,
                name="Real Worker Earnings (Production Workers)",
                line=dict(color="#6366f1", width=3.5),
                hovertemplate="%{y:.1f}",
            ))
        except Exception:
            pass

    # Policy shading — end dates are always "today" for ongoing periods
    fig.add_vrect(x0="2022-03-01", x1="2023-07-31",
                  fillcolor="rgba(59, 130, 246, 0.12)", layer="below", line_width=0)
    fig.add_annotation(
        x="2022-10-01", y=124,
        text="<b>FED HIKES</b><br><span style='font-size:8px'>0% → 5.5%</span>",
        showarrow=False,
        font=dict(size=9, color="#3b82f6"),
        bgcolor="rgba(10, 14, 26, 0.8)", bordercolor="#3b82f6",
        borderwidth=1.5, borderpad=4, align="center",
    )

    fig.add_vrect(x0="2024-09-01", x1=today,
                  fillcolor="rgba(16, 185, 129, 0.10)", layer="below", line_width=0)
    fig.add_annotation(
        x="2025-02-01", y=99,
        text="<b>FED CUTS</b><br><span style='font-size:8px'>5.5% → 4.3%</span>",
        showarrow=False,
        font=dict(size=9, color="#10b981"),
        bgcolor="rgba(10, 14, 26, 0.8)", bordercolor="#10b981",
        borderwidth=1.5, borderpad=4, align="center",
    )

    fig.add_vrect(x0="2025-04-02", x1=today,
                  fillcolor="rgba(220, 38, 38, 0.18)", layer="below", line_width=0)
    fig.add_annotation(
        x="2025-08-01", y=122,
        text="<b>TARIFF ERA</b><br><span style='font-size:8px'>Liberation Day (Apr 2025)</span>",
        showarrow=False,
        font=dict(size=9, color="#dc2626"),
        bgcolor="rgba(10, 14, 26, 0.8)", bordercolor="#dc2626",
        borderwidth=1.5, borderpad=4, align="center",
    )

    # Baseline vline
    fig.add_vline(x=baseline, line_dash="dash",
                  line_color="rgba(255,255,255,0.15)", line_width=1.5)
    fig.add_annotation(
        x=baseline, y=127,
        text="Jan 2020", showarrow=False,
        font=dict(size=8, color=COLORS["text_secondary"]),
        bgcolor="rgba(30, 36, 51, 0.6)",
    )

    fig.update_layout(**{
        **DARK_TEMPLATE,
        "paper_bgcolor": COLORS["bg_secondary"],
        "plot_bgcolor":  COLORS["bg_secondary"],
        "font": dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
        "xaxis": dict(
            type="date", rangeselector=_rangeselector(),
            gridcolor="rgba(255,255,255,0.05)", color=COLORS["text_secondary"],
        ),
        "yaxis": dict(
            title=dict(text="<b>Index (Jan 2020 = 100)</b>",
                       font=dict(color="#e8eaed", size=11)),
            tickfont=dict(color="#9aa0b1", size=11),
            range=[94, 132], dtick=5, showgrid=True,
            gridcolor="rgba(255,255,255,0.07)",
        ),
        "hovermode": "x unified",
        "legend": dict(
            orientation="h", yanchor="bottom", y=-0.40, xanchor="center", x=0.5,
            bgcolor="rgba(30, 36, 51, 0.85)", bordercolor="#4b5563",
            borderwidth=1, font=dict(size=10, color=COLORS["text_primary"]),
        ),
        "margin": dict(l=70, r=40, t=35, b=100),
    })
    return fig


# ── Lens 3: Financial Stress ───────────────────────────────────────────────────
def create_market_lens(df):
    fig = go.Figure()
    baseline = pd.to_datetime("2020-01-01")
    sp_y = None

    # S&P 500 (indexed to baseline)
    if "SP500_RAW" in df.columns:
        try:
            s = df["SP500_RAW"].astype(float)
            base = float(s.asof(baseline))
            sp_y = (s / base) * 100.0
        except Exception:
            pass
    elif "SP500" in df.columns:
        sp_y = df["SP500"].astype(float)

    if sp_y is not None:
        fig.add_trace(go.Scatter(
            x=sp_y.index, y=sp_y,
            name="S&P 500",
            line=dict(color="#10b981", width=3),
            hovertemplate="%{y:.1f}",
        ))
        # Market peak annotation
        try:
            peak_date = sp_y.idxmax()
            peak_val  = float(sp_y.max())
            fig.add_annotation(
                x=peak_date, y=peak_val,
                text=f"<b>+{peak_val - 100:.0f}%</b><br><span style='font-size:8px'>since Jan 2020</span>",
                showarrow=True, arrowhead=2,
                arrowcolor="#10b981", arrowwidth=1.5,
                ax=40, ay=-30,
                font=dict(size=9, color=COLORS["text_primary"]),
                bgcolor="rgba(30, 36, 51, 0.85)",
                bordercolor="#10b981", borderwidth=1.5, borderpad=3,
            )
        except Exception:
            pass

    # Credit card delinquency (right axis)
    if "DRCCLACBS_RAW" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["DRCCLACBS_RAW"],
            name="Credit Card Delinquency (90+ days)",
            line=dict(color="#ef4444", width=2.5, dash="solid"),
            yaxis="y2", hovertemplate="%{y:.2f}%",
        ))

    # Consumer loan delinquency (right axis)
    if "DRCLACBS_RAW" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["DRCLACBS_RAW"],
            name="Consumer Loan Delinquency",
            line=dict(color="#ef4444", width=1.5, dash="dash"),
            yaxis="y2", hovertemplate="%{y:.2f}%",
        ))

    y_max = 220
    if sp_y is not None:
        try:
            y_max = max(y_max, float(sp_y.max()) * 1.08)
        except Exception:
            pass

    # Baseline vline
    fig.add_vline(x=baseline, line_dash="dash",
                  line_color="rgba(255,255,255,0.15)", line_width=1.5)
    fig.add_annotation(
        x=baseline, y=y_max * 0.95,
        text="Jan 2020", showarrow=False,
        font=dict(size=8, color=COLORS["text_secondary"]),
        bgcolor="rgba(30, 36, 51, 0.6)",
    )

    fig.update_layout(**{
        **DARK_TEMPLATE,
        "paper_bgcolor": COLORS["bg_secondary"],
        "plot_bgcolor":  COLORS["bg_secondary"],
        "font": dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
        "xaxis": dict(
            type="date", rangeselector=_rangeselector(),
            gridcolor="rgba(255,255,255,0.05)", color=COLORS["text_secondary"],
        ),
        "yaxis": dict(
            title=dict(text="<b>S&P 500 (Jan 2020 = 100)</b>",
                       font=dict(color="#10b981", size=11)),
            tickfont=dict(color=COLORS["text_secondary"], size=11),
            range=[70, y_max], showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
        ),
        "yaxis2": dict(
            overlaying="y", side="right", showgrid=False,
            title=dict(text="<b>Delinquency Rate (%)</b>",
                       font=dict(color="#ef4444", size=11)),
            tickfont=dict(color="#ef4444", size=11),
            range=[0.5, 4.5],
        ),
        "hovermode": "x unified",
        "legend": dict(
            orientation="h", yanchor="bottom", y=-0.40, xanchor="center", x=0.5,
            bgcolor="rgba(30, 36, 51, 0.85)", bordercolor="#4b5563",
            borderwidth=1, font=dict(size=10, color="#e8eaed"),
        ),
        "margin": dict(l=70, r=60, t=35, b=100),
    })
    return fig


# ── Lens 4: Wealth Distribution ────────────────────────────────────────────────
def create_wealth_lens(df):
    fig = go.Figure()

    series_map = [
        ("WEALTH_BOTTOM50_RAW", "Bottom 50%",  "#ef4444", "rgba(239, 68, 68, 0.5)"),
        ("WEALTH_NEXT40_RAW",   "Next 40%",    "#f59e0b", "rgba(245, 158, 11, 0.5)"),
        ("WEALTH_NEXT9_RAW",    "Next 9%",     "#3b82f6", "rgba(59, 130, 246, 0.5)"),
        ("WEALTH_99_999_RAW",   "Next 0.9%",   "#8b5cf6", "rgba(139, 92, 246, 0.5)"),
        ("WEALTH_TOP0_1_RAW",   "Top 0.1%",    "#10b981", "rgba(16, 185, 129, 0.5)"),
    ]
    ordered = ["Bottom 50%", "Next 40%", "Next 9%", "Next 0.9%", "Top 0.1%"]
    fill_map = {label: fill for (_, label, _, fill) in series_map}
    col_map  = {label: col  for (col, label, _, _) in series_map}

    resolved = {}
    for col, label, color, fill in series_map:
        if col in df.columns:
            try:
                s = df[col].astype(float).dropna()
                try:
                    s.index = s.index.to_timestamp() if hasattr(s.index, "to_timestamp") else pd.to_datetime(s.index.astype(str))
                except Exception:
                    s.index = pd.to_datetime(s.index.astype(str), errors="coerce")
                resolved[label] = s.rename(label)
            except Exception:
                pass

    if resolved:
        shares = pd.concat([resolved[l] for l in ordered if l in resolved], axis=1)
        shares = shares[[c for c in ordered if c in shares.columns]]
        for label in shares.columns:
            fig.add_trace(go.Scatter(
                x=shares.index, y=shares[label].values,
                name=label,
                line=dict(color="rgba(255,255,255,0.07)", width=0.5),
                mode="lines",
                stackgroup="one",
                fillcolor=fill_map.get(label),
                hovertemplate="%{y:.1f}%",
            ))
    else:
        fig.add_annotation(
            x=0.5, y=0.5, xref="paper", yref="paper",
            text="Wealth data not available", showarrow=False,
            font=dict(size=11, color=COLORS["text_secondary"]),
        )

    fig.update_layout(**{
        **DARK_TEMPLATE,
        "paper_bgcolor": COLORS["bg_secondary"],
        "plot_bgcolor":  COLORS["bg_secondary"],
        "font": dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
        "xaxis": dict(
            type="date", rangeselector=_rangeselector(),
            gridcolor="rgba(255,255,255,0.05)", color=COLORS["text_secondary"],
        ),
        "yaxis": dict(
            title=dict(text="<b>Share of Total U.S. Wealth (%)</b>",
                       font=dict(color=COLORS["text_primary"], size=11)),
            tickfont=dict(color=COLORS["text_secondary"], size=11),
            range=[0, 100], showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
        ),
        "hovermode": "x unified",
        "legend": dict(
            orientation="h", yanchor="bottom", y=-0.40, xanchor="center", x=0.5,
            bgcolor="rgba(30, 36, 51, 0.85)", bordercolor="#4b5563",
            borderwidth=1, font=dict(size=10, color="#e8eaed"),
        ),
        "margin": dict(l=60, r=40, t=35, b=100),
    })
    return fig
