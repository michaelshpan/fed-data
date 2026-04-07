import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FRED_API_KEY")
START_DATE = "2006-01-01"
END_DATE = "2025-12-31"
OUTPUT_CSV = "macro_panel_2006_2025_monthly.csv"

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "pce_price_index": "PCEPI",
    "core_pce_price_index": "PCEPILFE",
    "fed_funds_rate": "FEDFUNDS",
    "real_gdp_growth_annualized_qoq": "A191RL1Q225SBEA",
    "ust_10y_yield": "DGS10",
    "ust_2y_yield": "DGS2",
    "yield_curve_10y_2y": "T10Y2Y",
    "unemployment_rate": "UNRATE",
    "nonfarm_payrolls": "PAYEMS",
    "consumer_sentiment": "UMCSENT",
    "wti_oil_price": "DCOILWTICO",
    "initial_jobless_claims": "ICSA",
    "housing_starts": "HOUST",
    "baa_corp_spread_10y": "BAA10YM",
    "nfci": "NFCI",
}

AGGREGATION_METHOD = {
    "pce_price_index": "avg",
    "core_pce_price_index": "avg",
    "fed_funds_rate": "avg",
    "ust_10y_yield": "avg",
    "ust_2y_yield": "avg",
    "yield_curve_10y_2y": "avg",
    "unemployment_rate": "avg",
    "nonfarm_payrolls": "avg",
    "consumer_sentiment": "avg",
    "wti_oil_price": "avg",
    "initial_jobless_claims": "avg",
    "housing_starts": "avg",
    "baa_corp_spread_10y": "avg",
    "nfci": "avg",
}


def fetch_fred_series(
    series_id: str,
    start_date: str,
    end_date: str,
    frequency: str | None = None,
    aggregation_method: str | None = None,
) -> pd.Series:
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,
    }

    if frequency is not None:
        params["frequency"] = frequency

    if frequency is not None and aggregation_method is not None:
        params["aggregation_method"] = aggregation_method

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if "observations" not in payload:
        raise ValueError(f"Unexpected response for {series_id}: {payload}")

    df = pd.DataFrame(payload["observations"])
    if df.empty:
        return pd.Series(dtype="float64", name=series_id)

    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    s = df.set_index("date")["value"].sort_index()
    s.name = series_id
    return s


def align_to_month_end(s: pd.Series) -> pd.Series:
    s = s.copy()
    s.index = s.index.to_period("M").to_timestamp(how="end").normalize()
    s = s.groupby(level=0).last()
    return s


def align_quarterly_to_month_end(s: pd.Series) -> pd.Series:
    s = s.copy()
    s.index = s.index.to_period("Q").to_timestamp(how="end").normalize()
    s = s.groupby(level=0).last()
    return s


def build_monthly_panel() -> pd.DataFrame:
    monthly_index = pd.date_range(start=START_DATE, end=END_DATE, freq="ME")
    panel = pd.DataFrame(index=monthly_index)

    for col_name, series_id in SERIES.items():
        if col_name == "real_gdp_growth_annualized_qoq":
            s = fetch_fred_series(
                series_id=series_id,
                start_date=START_DATE,
                end_date=END_DATE,
                frequency=None,
                aggregation_method=None,
            )
            s = align_quarterly_to_month_end(s)
            s = s.reindex(panel.index).ffill()
        else:
            s = fetch_fred_series(
                series_id=series_id,
                start_date=START_DATE,
                end_date=END_DATE,
                frequency="m",
                aggregation_method=AGGREGATION_METHOD[col_name],
            )
            s = align_to_month_end(s)
            s = s.reindex(panel.index)

        panel[col_name] = s

    return panel


def add_transformations(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["pce_inflation_yoy_pct"] = out["pce_price_index"].pct_change(12) * 100
    out["core_pce_inflation_yoy_pct"] = out["core_pce_price_index"].pct_change(12) * 100
    out["nonfarm_payrolls_mom_change"] = out["nonfarm_payrolls"].diff()
    out["nonfarm_payrolls_3m_avg_change"] = (
        out["nonfarm_payrolls_mom_change"].rolling(3).mean()
    )
    out["wti_oil_yoy_pct"] = out["wti_oil_price"].pct_change(12) * 100

    return out


def main():
    if not API_KEY:
        raise ValueError(
            "FRED_API_KEY not found. Add it to your .env file or export it in your shell."
        )

    panel = build_monthly_panel()
    panel = add_transformations(panel)

    panel = panel.reset_index().rename(columns={"index": "date"})
    panel["date"] = panel["date"].dt.strftime("%Y-%m-%d")

    panel.to_csv(OUTPUT_CSV, index=False)

    print(f"Saved CSV: {OUTPUT_CSV}")
    print(f"Rows: {len(panel):,}")
    print(f"Columns: {len(panel.columns):,}")
    print(panel.head(12))
    print("\nMissing values by column:")
    print(panel.isna().sum())


if __name__ == "__main__":
    main()