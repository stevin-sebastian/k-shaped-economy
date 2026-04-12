START_DATE = "2017-01-01"
BASELINE = "2020-01-01"

# ── FRED Series IDs ────────────────────────────────────────────────────────────
SERIES_IDS = {
    # Macro
    "FEDFUNDS":        "FEDFUNDS",        # Federal Funds Rate (Monthly)
    "UNRATE":          "UNRATE",          # Unemployment Rate (Monthly)
    "PAYEMS":          "PAYEMS",          # Total Nonfarm Employment (Monthly)

    # Upper Arm — asset classes
    "SP500":           "SP500",           # S&P 500 (Daily)
    "HOME_PRICES":     "CSUSHPISA",       # Case-Shiller National Home Price Index (Monthly)

    # Lower Arm — workers
    "EMP_LOW_WAGE":    "USLAH",           # Leisure & Hospitality Employment (Monthly)
    # Production/Nonsupervisory workers (~80% of private workforce).
    # Avoids the composition bias in sector-specific earnings (e.g. L&H wages
    # spiked in 2020 because the lowest-paid workers were laid off first).
    "WAGE_LOW_WAGE":   "CES0500000008",   # Prod. & Nonsupervisory Workers Avg Hourly Earnings (Monthly)

    # Prices
    "CPIAUCSL":        "CPIAUCSL",        # CPI All Urban Consumers (Monthly)

    # Credit stress
    "DRCCLACBS":       "DRCCLACBS",       # Credit Card Delinquency Rate 90+ days (Quarterly)
    "DRCLACBS":        "DRCLACBS",        # Consumer Loan Delinquency Rate (Quarterly)

    # Wealth distribution — Federal Reserve Distributional Financial Accounts
    "WEALTH_TOP1":     "WFRBST01134",     # Top 1% wealth share (Quarterly)
    "WEALTH_TOP0_1":   "WFRBSTP1300",     # Top 0.1% wealth share (Quarterly)
    "WEALTH_99_999":   "WFRBS99T999273",  # 99–99.9% wealth share (Quarterly)
    "WEALTH_NEXT9":    "WFRBSN09161",     # 90–99th percentile wealth share (Quarterly)
    "WEALTH_NEXT40":   "WFRBSN40188",     # 50–90th percentile wealth share (Quarterly)
    "WEALTH_BOTTOM50": "WFRBSB50215",     # Bottom 50% wealth share (Quarterly)
}

# ── Human-readable labels ──────────────────────────────────────────────────────
SERIES_NAMES = {
    "FEDFUNDS":        "Fed Funds Rate (%)",
    "UNRATE":          "Unemployment Rate (%)",
    "PAYEMS":          "Total Nonfarm Employment (Thousands)",
    "SP500":           "S&P 500 Index",
    "HOME_PRICES":     "U.S. Home Price Index (Case-Shiller)",
    "EMP_LOW_WAGE":    "Leisure & Hospitality Employment (Thousands)",
    "WAGE_LOW_WAGE":   "Production Workers Avg Hourly Earnings ($)",
    "CPIAUCSL":        "CPI (All Urban Consumers)",
    "DRCCLACBS":       "Credit Card Delinquency Rate (%)",
    "DRCLACBS":        "Consumer Loan Delinquency Rate (%)",
    "WEALTH_TOP1":     "Top 1% Wealth Share (%)",
    "WEALTH_TOP0_1":   "Top 0.1% Wealth Share (%)",
    "WEALTH_99_999":   "99–99.9% Wealth Share (%)",
    "WEALTH_NEXT9":    "90–99th Percentile Wealth Share (%)",
    "WEALTH_NEXT40":   "50–90th Percentile Wealth Share (%)",
    "WEALTH_BOTTOM50": "Bottom 50% Wealth Share (%)",
}

# ── Data sources ───────────────────────────────────────────────────────────────
DATA_SOURCES = {
    "Primary":    "FRED (Federal Reserve Economic Data)",
    "Wealth":     "Federal Reserve Distributional Financial Accounts (DFA)",
    "Employment": "Bureau of Labor Statistics (BLS) via FRED",
    "Markets":    "S&P Dow Jones Indices / Case-Shiller via FRED",
}

# ── Illustrative tariff timeline ───────────────────────────────────────────────
# Simplified weighted-average effective US tariff rate for visualization only.
# Not official BLS/USTR data. Sources: PIIE, Peterson Institute estimates.
TARIFF_SCHEDULE = [
    ("2017-01-01", 2.4),   # Baseline pre-trade-war effective tariff rate
    ("2018-07-06", 12.0),  # Trade war escalation (China Section 301 tariffs)
    ("2020-01-15", 10.0),  # Phase One deal partial rollback
    ("2025-04-02", 22.0),  # Liberation Day — weighted avg effective rate (est.)
]

# ── Color palette ──────────────────────────────────────────────────────────────
COLORS = {
    "bg_primary":    "#0a0e1a",
    "bg_secondary":  "#141824",
    "bg_tertiary":   "#1e2433",
    "text_primary":  "#e8eaed",
    "text_secondary":"#9aa0b1",
    "border_subtle": "#2d3748",
    "upper_arm":     "#10b981",  # emerald — assets, markets
    "lower_arm":     "#ef4444",  # red — labor stress, delinquency
    "neutral":       "#6366f1",  # indigo — unemployment, neutral
    "inflation":     "#f59e0b",  # amber — prices, tariffs
    "fed":           "#3b82f6",  # blue — Fed policy
    "market":        "#8b5cf6",  # purple — S&P milestones
    # aliases kept for backwards compatibility
    "accent_upper":  "#10b981",
    "accent_lower":  "#ef4444",
    "accent_neutral":"#6366f1",
    "event_fed":     "#3b82f6",
    "event_tariff":  "#dc2626",
    "event_shock":   "#f97316",
    "event_market":  "#8b5cf6",
    "tariff":        "#dc2626",
}

# ── Misc ───────────────────────────────────────────────────────────────────────
BRANCH_DATE = "2020-03-01"   # visual K-branch start
DEBUG_WEALTH = False
DEBUG_WEALTH_OUTPUT = "data/wealth_debug.csv"
