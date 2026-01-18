"""Single module to extract financial data from Yahoo Finance API."""

import os

import awswrangler as wr
import boto3
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

ambiente = os.environ.get("AMBIENTE")
bucket_name = os.environ.get("S3_BUCKET")

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
    df = df.stack().reset_index()
    df.columns.name = None
    df.columns = [column.lower().strip().replace(" ", "_") for column in df.columns]
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df


def main():
    """Extract, transform and load financial data to S3."""
    df = yfinance_handler(tickers)
    path = f"s3://{bucket_name}/raw/"

    wr.s3.to_parquet(
        df=df.copy(),
        path=path,
        dataset=True,
        use_threads=True,
        partition_cols=["date"],
        mode="overwrite_partitions",
    )
    cliente = boto3.client("s3")
    cliente.put_object(Bucket=bucket_name, Key="raw/trigger_lambda.txt", Body="")


if __name__ == "__main__":
    main()
