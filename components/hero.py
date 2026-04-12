import pandas as pd
import plotly.graph_objects as go
from data import config as data_config
from .lenses import DARK_TEMPLATE, _rangeselector

COLORS = data_config.COLORS


def create_k_timeline(df):
    """
    Hero chart: two composite K-shaped indices (Jan 2020 = 100).
    Upper Arm — equities + home prices.
    Lower Arm — L&H employment + real worker wages + inverted delinquency + bottom-50% wealth.
    """
    fig = go.Figure()

    upper = df["K_UPPER"] if "K_UPPER" in df.columns else None
    lower = df["K_LOWER"] if "K_LOWER" in df.columns else None

    if upper is not None and lower is not None:
        # Lower arm first so upper fills tonexty against it
        fig.add_trace(go.Scatter(
            x=lower.index, y=lower,
            name="Lower Arm — Workers & Debt",
            line=dict(color=COLORS["lower_arm"], width=3.5),
            fill="tozeroy",
            fillcolor="rgba(239, 68, 68, 0.06)",
            hovertemplate="Lower: %{y:.1f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=upper.index, y=upper,
            name="Upper Arm — Assets & Markets",
            line=dict(color=COLORS["upper_arm"], width=3.5),
            fill="tonexty",
            fillcolor="rgba(16, 185, 129, 0.10)",
            hovertemplate="Upper: %{y:.1f}<extra></extra>",
        ))

    # Baseline reference
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.12)")
    fig.add_vline(x=pd.to_datetime("2020-01-01"), line_dash="dash",
                  line_color="rgba(255,255,255,0.15)", line_width=1.5)
    fig.add_annotation(
        x=pd.to_datetime("2020-01-01"),
        y=(upper.max() if upper is not None else 160),
        text="Jan 2020<br>baseline",
        showarrow=False,
        font=dict(size=8, color=COLORS["text_secondary"]),
        bgcolor="rgba(30, 36, 51, 0.7)",
        xanchor="left", xshift=6,
    )

    # COVID shock marker
    fig.add_vline(x=pd.to_datetime("2020-03-15"), line_dash="dot",
                  line_color="rgba(249,115,22,0.4)", line_width=1)
    fig.add_annotation(
        x=pd.to_datetime("2020-03-15"),
        y=75,
        text="COVID-19<br>shock",
        showarrow=False,
        font=dict(size=8, color="#f97316"),
        bgcolor="rgba(30, 36, 51, 0.7)",
        xanchor="left", xshift=6,
    )

    # Divergence callout — placed dynamically at the end of the data
    if upper is not None and lower is not None:
        try:
            last_date  = upper.dropna().index[-1]
            last_upper = float(upper.dropna().iloc[-1])
            last_lower = float(lower.dropna().iloc[-1])
            gap = last_upper - last_lower
            fig.add_annotation(
                x=last_date,
                y=(last_upper + last_lower) / 2,
                text=f"<b>Gap: {gap:.0f} pts</b>",
                showarrow=False,
                xanchor="right", xshift=-8,
                font=dict(size=10, color="#e8eaed"),
                bgcolor="rgba(30, 36, 51, 0.85)",
                bordercolor="#4b5563", borderwidth=1, borderpad=4,
            )
        except Exception:
            pass

    fig.update_layout(**{
        **DARK_TEMPLATE,
        "paper_bgcolor": COLORS["bg_secondary"],
        "plot_bgcolor":  COLORS["bg_secondary"],
        "font": dict(color=COLORS["text_primary"], family="Inter, sans-serif"),
        "xaxis": dict(
            type="date", rangeselector=_rangeselector(),
            gridcolor="rgba(255,255,255,0.04)", color=COLORS["text_secondary"],
            showline=True, linecolor=COLORS["border_subtle"],
        ),
        "yaxis": dict(
            title=dict(text="<b>Composite Index (Jan 2020 = 100)</b>",
                       font=dict(color="#e8eaed", size=12)),
            tickfont=dict(color="#9aa0b1", size=11),
            gridcolor="rgba(255,255,255,0.05)", zeroline=False,
        ),
        "hovermode": "x unified",
        "legend": dict(
            orientation="h", yanchor="bottom", y=-0.30,
            xanchor="center", x=0.5,
            bgcolor="rgba(30, 36, 51, 0.85)",
            bordercolor="#4b5563", borderwidth=1,
            font=dict(size=11, color=COLORS["text_primary"]),
        ),
        "margin": dict(l=60, r=40, t=20, b=80),
    })
    return fig
