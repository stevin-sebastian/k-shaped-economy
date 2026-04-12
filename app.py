import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, ctx

from data.loader import get_all_data
from data.processor import (
    rebase_series, calculate_k_indices, align_to_monthly,
    compute_real_wages_and_cpi,
)
from data import config as data_config
from components.hero import create_k_timeline
from components.lenses import (
    create_labor_lens, create_price_lens,
    create_market_lens, create_wealth_lens,
)

# ── App init ───────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = "K-Shaped Economy"
server = app.server


# ── Data pipeline ──────────────────────────────────────────────────────────────
def load_and_process_data():
    df = get_all_data()
    df_monthly = align_to_monthly(df)
    df_raw = compute_real_wages_and_cpi(df_monthly)
    df_rebased = rebase_series(df_raw, data_config.BASELINE)

    # Attach raw columns with _RAW suffix so chart functions can access original units
    for col in df_raw.columns:
        df_rebased[f"{col}_RAW"] = df_raw[col]

    return calculate_k_indices(df_rebased)


df_global = load_and_process_data()
DATA_UPDATED = pd.Timestamp.now().strftime("%B %d, %Y")


# ── Helpers ────────────────────────────────────────────────────────────────────
def _set_height(fig, height):
    fig.update_layout(height=height)
    return fig


def _apply_common(fig, height, x_start=None):
    """Apply consistent layout to every figure."""
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    start = x_start or data_config.START_DATE
    _set_height(fig, height)
    fig.update_layout(hovermode="x unified", margin=dict(l=60, r=60, t=30, b=100))
    fig.update_layout(legend=dict(y=-0.40))
    fig.update_xaxes(range=[start, today])
    return fig


def _build_all_figures(x_start=None):
    return {
        "hero":   _apply_common(create_k_timeline(df_global),   450, x_start),
        "labor":  _apply_common(create_labor_lens(df_global),   320, x_start),
        "price":  _apply_common(create_price_lens(df_global),   320, x_start),
        "market": _apply_common(create_market_lens(df_global),  320, x_start),
        "wealth": _apply_common(create_wealth_lens(df_global),  320, x_start),
    }


_figs = _build_all_figures()


# ── Layout helpers ─────────────────────────────────────────────────────────────
LABEL_STYLE = {"color": "#9aa0b1", "fontSize": "11px",
               "fontWeight": "600", "letterSpacing": "0.05em"}
VALUE_STYLE = {"color": "#e8eaed", "fontSize": "11px"}
WARN_STYLE  = {"color": "#f59e0b", "fontSize": "11px"}

GRAPH_CONFIG = {"displayModeBar": False}


def _lens_card(lens_id, title, subtitle, graph_id, figure, desc_content):
    return html.Div([
        # Header
        html.Div([
            html.Span(
                f"LENS {lens_id}  " if str(lens_id).upper() != "HERO" else "",
                style={"color": "#4b5563", "fontSize": "11px",
                       "fontWeight": "700", "letterSpacing": "0.1em"},
            ),
            html.Span(title, style={"color": "#e8eaed", "fontSize": "17px",
                                    "fontWeight": "600"}),
            html.P(subtitle, style={"color": "#6b7280", "fontSize": "12px",
                                    "fontStyle": "italic", "marginTop": "2px",
                                    "marginBottom": "0", "lineHeight": "1.4"}),
        ], style={"marginBottom": "0.6rem"}),

        # Chart
        dcc.Graph(id=graph_id, figure=figure, config=GRAPH_CONFIG,
                  style={"height": "320px", "marginBottom": "0.75rem"}),

        # Description box
        html.Div(desc_content, style={
            "backgroundColor": "rgba(20, 24, 36, 0.6)",
            "padding": "10px 14px",
            "borderRadius": "6px",
            "borderLeft": "3px solid #2d3748",
            "fontSize": "11.5px",
            "lineHeight": "1.45",
            "color": "#9aa0b1",
        }),
    ], style={"padding": "0.5rem"})


def _bullet(color, label, detail):
    return html.Div([
        html.Span("━ ", style={"color": color, "fontSize": "13px", "fontWeight": "bold"}),
        html.Span(label + ": ", style={"color": "#e8eaed", "fontWeight": "600"}),
        html.Span(detail, style={"color": "#9aa0b1"}),
    ], style={"marginBottom": "4px"})


def _warn(text):
    return html.Div([
        html.Span("⚠ ", style={"color": "#f59e0b"}),
        html.Span(text, style={"color": "#f59e0b", "fontStyle": "italic"}),
    ], style={"marginTop": "4px"})


# ── Period selector ────────────────────────────────────────────────────────────
period_selector = html.Div([
    html.Span("VIEW  ", style={"color": "#4b5563", "fontSize": "11px",
                                "fontWeight": "700", "letterSpacing": "0.1em",
                                "verticalAlign": "middle", "marginRight": "6px"}),
    dbc.RadioItems(
        id="period-selector",
        options=[
            {"label": "Full (2017+)",       "value": "full"},
            {"label": "Post-COVID (2020+)", "value": "2020"},
            {"label": "Recent (2022+)",     "value": "2022"},
        ],
        value="full",
        className="btn-group",
        inputClassName="btn-check",
        labelClassName="btn btn-outline-secondary btn-sm period-btn",
        labelCheckedClassName="btn btn-secondary btn-sm period-btn active",
        inline=True,
    ),
], style={"textAlign": "right", "marginBottom": "0.75rem"})


# ── Layout ─────────────────────────────────────────────────────────────────────
app.layout = dbc.Container([

    # ── Header ────────────────────────────────────────────────────────────────
    dbc.Row(dbc.Col(html.Header([
        html.H1("The K-Shaped Economy",
                style={"color": "#e8eaed", "fontSize": "26px",
                       "fontWeight": "700", "marginBottom": "4px"}),
        html.H2("Two Economies, One Nation: Asset Holders vs. Working-Class America (2017 – Present)",
                style={"color": "#9aa0b1", "fontSize": "14px",
                       "fontWeight": "400", "marginBottom": "6px"}),
        html.P("Four analytical lenses: Labor · Affordability · Financial Stress · Wealth Distribution",
               style={"color": "#4b5563", "fontSize": "12px",
                      "fontStyle": "italic", "marginBottom": "0"}),
    ], className="k-header")), className="mb-3"),

    # ── Period selector ───────────────────────────────────────────────────────
    dbc.Row(dbc.Col(period_selector, width=12)),

    # ── Hero chart ────────────────────────────────────────────────────────────
    dbc.Row(dbc.Col(
        _lens_card(
            "HERO", "K-Divergence Timeline",
            "Composite upper arm (assets & markets) vs. lower arm (workers & debt), indexed Jan 2020 = 100",
            "hero-chart", _figs["hero"],
            html.Div([
                html.Div("How the composite indices are built:",
                         style={"color": "#e8eaed", "fontWeight": "600",
                                "marginBottom": "5px"}),
                _bullet("#10b981", "Upper Arm",
                        "Average of S&P 500 and Case-Shiller home prices — "
                        "the two asset classes most concentrated among wealthier households"),
                _bullet("#ef4444", "Lower Arm",
                        "Average of Leisure & Hospitality employment, real production-worker "
                        "earnings, inverted delinquency rate, and bottom-50% wealth share"),
                html.P("All series indexed to Jan 2020 = 100. A rising gap means asset holders "
                       "outpaced workers in cumulative gains since COVID.",
                       style={"color": "#6b7280", "fontSize": "10.5px",
                              "fontStyle": "italic", "marginTop": "6px",
                              "marginBottom": "0"}),
            ]),
        ),
        width={"size": 10, "offset": 1},
    ), className="mb-4"),

    # ── 2×2 lens grid ─────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col(_lens_card(
            "1", "Labor Reality",
            "Headline unemployment masked prolonged pain in low-wage sectors",
            "labor-chart", _figs["labor"],
            html.Div([
                _bullet("#6366f1", "Unemployment Rate",
                        "Headline metric — recovered to pre-COVID levels by mid-2022"),
                _bullet("#10b981", "Total Nonfarm Employment",
                        "Aggregate job recovery rebounded quickly post-stimulus"),
                _bullet("#ef4444", "Leisure & Hospitality Employment",
                        "Restaurants, hotels, entertainment — lost 49% of jobs in Apr 2020 "
                        "and lagged the headline recovery by 18+ months"),
                html.Hr(style={"borderColor": "#2d3748", "margin": "6px 0"}),
                html.P("Note: Official unemployment understates precarity by excluding "
                       "gig workers, part-time workers seeking full-time work, and discouraged "
                       "workers who left the labor force.",
                       style={"color": "#6b7280", "fontSize": "10.5px",
                              "fontStyle": "italic", "marginBottom": "0"}),
            ]),
        ), width=6),

        dbc.Col(_lens_card(
            "2", "Policy vs. Affordability",
            "Inflation eroded real purchasing power even as nominal wages rose",
            "price-chart", _figs["price"],
            html.Div([
                _bullet("#f59e0b", "Consumer Prices (CPI)",
                        "Cost of living — up 20%+ since Jan 2020"),
                _bullet("#6366f1", "Real Worker Earnings",
                        "Production/nonsupervisory wages deflated by CPI — "
                        "flat to slightly negative since 2020, meaning workers earned more "
                        "dollars but bought less"),
                html.Hr(style={"borderColor": "#2d3748", "margin": "6px 0"}),
                html.P("Shaded regions show Fed rate-hike cycle (Mar 2022 – Jul 2023), "
                       "the subsequent cut cycle (Sep 2024+), and the Liberation Day "
                       "tariff era (Apr 2025+). Tariff effective-rate estimates from PIIE.",
                       style={"color": "#6b7280", "fontSize": "10.5px",
                              "fontStyle": "italic", "marginBottom": "0"}),
            ]),
        ), width=6),
    ], className="mb-3"),

    dbc.Row([
        dbc.Col(_lens_card(
            "3", "Financial Stress",
            "Markets soared while consumer debt delinquencies climbed",
            "market-chart", _figs["market"],
            html.Div([
                _bullet("#10b981", "S&P 500",
                        "Stock market index — up 80–100% since Jan 2020, reaching record highs "
                        "in 2024–25. ~57% of Americans own equities, but the top 10% hold ~93% "
                        "of all stock wealth."),
                _bullet("#ef4444", "Credit Card Delinquency (90+ days)",
                        "Rose from historic lows during stimulus to post-2010 highs by 2024"),
                _bullet("#ef4444", "Consumer Loan Delinquency",
                        "Broader consumer debt stress tracking upward in parallel"),
                html.Hr(style={"borderColor": "#2d3748", "margin": "6px 0"}),
                html.P("The divergence: markets recovered and surged (benefiting asset holders) "
                       "while debt stress accumulated for lower-income households squeezed by "
                       "inflation and rate hikes.",
                       style={"color": "#6b7280", "fontSize": "10.5px",
                              "fontStyle": "italic", "marginBottom": "0"}),
            ]),
        ), width=6),

        dbc.Col(_lens_card(
            "4", "Wealth Distribution",
            "Extreme concentration: top 10% own ~70% of wealth; bottom 50% own ~3%",
            "wealth-chart", _figs["wealth"],
            html.Div([
                html.P("Federal Reserve Distributional Financial Accounts (DFA) — quarterly.",
                       style={"color": "#6b7280", "fontSize": "10.5px",
                              "fontStyle": "italic", "marginBottom": "6px"}),
                _bullet("#10b981", "Top 0.1%",   "~13–14% of all U.S. wealth"),
                _bullet("#8b5cf6", "Next 0.9%",  "~16–18% of all U.S. wealth"),
                _bullet("#3b82f6", "Next 9%",    "~36–38% of all U.S. wealth (top 10% total: ~70%)"),
                _bullet("#f59e0b", "Next 40%",   "~28–30% of all U.S. wealth"),
                _bullet("#ef4444", "Bottom 50%", "~2–3% of all U.S. wealth"),
                html.Hr(style={"borderColor": "#2d3748", "margin": "6px 0"}),
                html.P("The bottom half of Americans share roughly the same slice of national "
                       "wealth as a rounding error in the top 0.1%'s portfolio.",
                       style={"color": "#6b7280", "fontSize": "10.5px",
                              "fontStyle": "italic", "marginBottom": "0"}),
            ]),
        ), width=6),
    ], className="mb-4"),

    # ── Footer ────────────────────────────────────────────────────────────────
    dbc.Row(dbc.Col(html.Div([
        html.Hr(style={"borderColor": "#2d3748"}),
        html.P([
            html.Span("Data sources: ", style={"color": "#6b7280", "fontWeight": "600"}),
            html.Span("FRED (Federal Reserve Economic Data) · BLS · "
                      "S&P Dow Jones Indices · Case-Shiller · "
                      "Federal Reserve DFA · PIIE (tariff estimates)",
                      style={"color": "#4b5563"}),
            html.Span(f"   ·   Last fetched: {DATA_UPDATED}",
                      style={"color": "#4b5563"}),
        ], style={"fontSize": "11px", "marginBottom": "0", "textAlign": "center"}),
    ])), className="mb-4"),

], fluid=True, style={"backgroundColor": data_config.COLORS["bg_primary"],
                       "minHeight": "100vh", "padding": "1.5rem"})


# ── Callback: sync all charts when period button changes ──────────────────────
@app.callback(
    Output("hero-chart",   "figure"),
    Output("labor-chart",  "figure"),
    Output("price-chart",  "figure"),
    Output("market-chart", "figure"),
    Output("wealth-chart", "figure"),
    Input("period-selector", "value"),
    prevent_initial_call=True,
)
def update_period(period):
    start_map = {
        "full": data_config.START_DATE,
        "2020": "2020-01-01",
        "2022": "2022-01-01",
    }
    start = start_map.get(period, data_config.START_DATE)
    figs  = _build_all_figures(x_start=start)
    return (
        figs["hero"], figs["labor"],
        figs["price"], figs["market"], figs["wealth"],
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
