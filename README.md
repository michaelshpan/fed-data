# fed-data

A Python script that pulls key U.S. macroeconomic indicators from the [FRED API](https://fred.stlouisfed.org/) (Federal Reserve Bank of St. Louis) and assembles them into a single monthly panel CSV.

## Data Sources

All data is pulled from FRED via their public REST API (`api.stlouisfed.org`). The following series are included:

| Column | FRED Series | Description |
|---|---|---|
| `pce_price_index` | PCEPI | PCE Price Index |
| `core_pce_price_index` | PCEPILFE | Core PCE Price Index (ex food & energy) |
| `fed_funds_rate` | FEDFUNDS | Effective Federal Funds Rate |
| `real_gdp_growth_annualized_qoq` | A191RL1Q225SBEA | Real GDP Growth (annualized, quarter-over-quarter) |
| `ust_10y_yield` | DGS10 | 10-Year Treasury Yield |
| `ust_2y_yield` | DGS2 | 2-Year Treasury Yield |
| `yield_curve_10y_2y` | T10Y2Y | 10Y-2Y Treasury Spread |
| `unemployment_rate` | UNRATE | Civilian Unemployment Rate |
| `nonfarm_payrolls` | PAYEMS | Total Nonfarm Payrolls |
| `consumer_sentiment` | UMCSENT | University of Michigan Consumer Sentiment |
| `wti_oil_price` | DCOILWTICO | WTI Crude Oil Price |
| `initial_jobless_claims` | ICSA | Initial Jobless Claims |
| `housing_starts` | HOUST | Housing Starts |
| `baa_corp_spread_10y` | BAA10YM | Baa Corporate Bond Spread over 10Y Treasury |
| `nfci` | NFCI | Chicago Fed National Financial Conditions Index |

## Aggregation

- **Monthly series** (most indicators): daily or weekly observations are aggregated to monthly frequency using the **average** for each month via the FRED API's built-in aggregation.
- **Quarterly series** (real GDP growth): fetched at native quarterly frequency, aligned to quarter-end dates, and **forward-filled** to populate each month within the quarter.
- All series are aligned to **month-end dates**.

## Derived Columns

The script computes several transformations on top of the raw series:

| Column | Calculation |
|---|---|
| `pce_inflation_yoy_pct` | Year-over-year % change in PCE Price Index |
| `core_pce_inflation_yoy_pct` | Year-over-year % change in Core PCE Price Index |
| `nonfarm_payrolls_mom_change` | Month-over-month change in nonfarm payrolls |
| `nonfarm_payrolls_3m_avg_change` | 3-month rolling average of payrolls change |
| `wti_oil_yoy_pct` | Year-over-year % change in WTI oil price |

## Output

The script outputs `macro_panel_2006_2025_monthly.csv` — a panel covering **January 2006 through December 2025** with one row per month.

## Setup

1. Get a free API key from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Create a `.env` file in the project root:
   ```
   FRED_API_KEY=your_key_here
   ```
3. Install dependencies:
   ```bash
   pip install requests pandas python-dotenv
   ```

## Usage

```bash
python macro_fred_export.py
```

This will fetch all series from FRED and write the output CSV to the current directory.
