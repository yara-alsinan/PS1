"""Create a compact, documented dataset for the Stock Sense website."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "data" / "processed"

# Three recognizable companies from each of the 11 S&P 500 sectors.
SYMBOLS = [
    "AAPL", "MSFT", "NVDA",  # Information Technology
    "GOOGL", "META", "NFLX",  # Communication Services
    "AMZN", "TSLA", "HD",  # Consumer Discretionary
    "WMT", "COST", "KO",  # Consumer Staples
    "JNJ", "UNH", "LLY",  # Health Care
    "JPM", "V", "BAC",  # Financials
    "CAT", "GE", "HON",  # Industrials
    "XOM", "CVX", "COP",  # Energy
    "NEE", "DUK", "SO",  # Utilities
    "PLD", "AMT", "EQIX",  # Real Estate
    "LIN", "APD", "SHW",  # Materials
]
START_DATE = "2021-01-01"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    companies = pd.read_csv(RAW_DIR / "sp500_companies.csv")
    company_columns = ["symbol", "company", "sector", "sub_industry", "headquarters", "founded"]
    companies = companies.loc[companies["symbol"].isin(SYMBOLS), company_columns]

    stocks = pd.read_csv(
        RAW_DIR / "sp500_stocks.csv",
        parse_dates=["date"],
        usecols=["date", "open", "high", "low", "close", "volume", "symbol"],
    )
    stocks = stocks.loc[(stocks["symbol"].isin(SYMBOLS)) & (stocks["date"] >= START_DATE)].copy()
    stocks = stocks.sort_values(["symbol", "date"])

    by_stock = stocks.groupby("symbol", group_keys=False)
    stocks["return_1d_pct"] = by_stock["close"].pct_change() * 100
    stocks["return_5d_pct"] = by_stock["close"].pct_change(5) * 100
    stocks["return_1m_pct"] = by_stock["close"].pct_change(21) * 100
    stocks["return_1y_pct"] = by_stock["close"].pct_change(252) * 100
    stocks["avg_volume_30d"] = by_stock["volume"].transform(lambda values: values.rolling(30, min_periods=10).mean())
    stocks["volume_vs_30d_avg"] = stocks["volume"] / stocks["avg_volume_30d"]
    stocks["high_52w"] = by_stock["close"].transform(lambda values: values.rolling(252, min_periods=30).max())
    stocks["drawdown_from_52w_high_pct"] = ((stocks["close"] / stocks["high_52w"]) - 1) * 100
    stocks["dip_flag"] = (
        (stocks["return_1d_pct"] <= -5)
        & (stocks["volume_vs_30d_avg"] >= 1.25)
    )

    output = stocks.merge(companies, on="symbol", how="left", validate="many_to_one")
    output = output[
        [
            "date", "symbol", "company", "sector", "sub_industry", "headquarters", "founded",
            "open", "high", "low", "close", "volume", "return_1d_pct", "return_5d_pct",
            "return_1m_pct", "return_1y_pct", "avg_volume_30d", "volume_vs_30d_avg", "high_52w",
            "drawdown_from_52w_high_pct", "dip_flag",
        ]
    ]
    output = output.round({
        "open": 2, "high": 2, "low": 2, "close": 2, "volume": 0, "return_1d_pct": 2,
        "return_5d_pct": 2, "return_1m_pct": 2, "return_1y_pct": 2, "avg_volume_30d": 0,
        "volume_vs_30d_avg": 2, "high_52w": 2, "drawdown_from_52w_high_pct": 2,
    })
    output.to_csv(OUTPUT_DIR / "stock_sense_data.csv", index=False, date_format="%Y-%m-%d")
    companies.to_csv(OUTPUT_DIR / "stock_sense_companies.csv", index=False)

    print(f"Wrote {len(output):,} daily records for {output['symbol'].nunique()} companies.")
    print(f"Date range: {output['date'].min():%Y-%m-%d} to {output['date'].max():%Y-%m-%d}")
    print(f"Dip-watch records: {int(output['dip_flag'].sum()):,}")


if __name__ == "__main__":
    main()
