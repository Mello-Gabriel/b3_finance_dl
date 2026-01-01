"""Single module to extract financial data from Yahoo Finance API."""

import os

import awswrangler as wr
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

ambiente = os.environ.get("AMBIENTE")

tickers = [
    "BOVA11.SA",
    "VALE3.SA",
    "ITUB4.SA",
    "PETR4.SA",
    "BBDC4.SA",
    "ELET3.SA",
    "PETR3.SA",
    "SBSP3.SA",
    "BPAC11.SA",
    "WEGE3.SA",
    "B3SA3.SA",
    "ITSA4.SA",
    "EMBR3.SA",
    "BBAS3.SA",
    "ABEV3.SA",
    "EQTL3.SA",
    "RDOR3.SA",
    "RENT3.SA",
    "ENEV3.SA",
    "SUZB3.SA",
]


def yfinance_handler(tickers: list[str]) -> pd.DataFrame:
    """Get financial data from Yahoo Finance API."""
    yf_ticker = yf.Tickers(tickers)
    df = yf_ticker.history(period="1y", interval="1d")
    df = df.stack(level=0, future_stack=True).reset_index()
    df = df.rename(columns={"level_0": "ticker"})
    df.columns.name = None
    df.columns = [column.lower().strip().replace(" ", "_") for column in df.columns]
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df


def main():
    """Extract, transform and load financial data to S3."""
    df = yfinance_handler(tickers)
    df = df.rename(columns={"date": "Date"})
    bucket_name = os.environ.get("S3_BUCKET")
    path = f"s3://{bucket_name}/raw/"

    wr.s3.to_parquet(
        df=df.copy(),
        path=path,
        dataset=True,
        use_threads=True,
        partition_cols=["Date"],
        mode="overwrite_partitions",
    )


if __name__ == "__main__":
    main()
