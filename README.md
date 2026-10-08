# The K-Shaped Economy

An interactive dashboard of the post-2017 US economy, built to show the "K-shaped" divergence: asset holders and top wealth on the upper arm, wage earners and household balance sheets on the lower arm.

Built with Python, Dash and Plotly for the Data Visualisation module of the MSc in Computer Science at Trinity College Dublin (2025).

## What it shows

A hero timeline plots two composite indices, `K_UPPER` and `K_LOWER`, from 2017 onwards. Four lenses then break the divergence down:

| Lens | Compares |
|---|---|
| Labour reality | unemployment, total employment and low-wage (leisure and hospitality) employment |
| Policy vs affordability | CPI against real low-wage earnings, with rate hikes, cuts and tariffs shaded |
| Financial stress | the S&P 500 against credit card and consumer loan delinquencies |
| Wealth distribution | wealth shares of the top 0.1%, next 0.9%, next 9%, next 40% and bottom 50% |

## How the data pipeline works

1. **Load** the configured FRED time series into one date-indexed frame (`data/loader.py`).
2. **Align** mixed-frequency series, such as the daily S&P 500, to monthly.
3. **Deflate** wages by CPI to get real earnings.
4. **Rebase** every series to a common baseline so they share one scale, keeping the raw units alongside for hover text.
5. **Compute** the `K_UPPER` and `K_LOWER` composites (`data/processor.py`). Missing series degrade the composite instead of breaking it.

Data is loaded once at start-up and every figure is pre-built, so callbacks stay light.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:8050.

## Layout

```
app.py              entry point: load data, build figures, declare the layout
data/               loading, configuration, events, feature engineering
components/         Plotly figure factories for the hero timeline and the lenses
assets/             CSS
Procfile            for deployment on Render
```
