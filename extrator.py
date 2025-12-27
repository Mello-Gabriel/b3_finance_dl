import pandas as pd
import yfinance as yf
import boto3
import io


def lambda_handler(event, context):
    buffer = io.BytesIO()

    dados_acoes = ["PETR4.SA", "SUZ"]

    download = yf.download(dados_acoes, period="1d")

    download = download.stack().reset_index()

    download["Date"] = download["Date"].astype(str)

    date_ref = download["Date"].iloc[0]

    file_name = f"raw/Date={date_ref}/raw_data.parquet"

    download.columns = [column.lower().replace(" ", "_") for column in download.columns]

    download.to_parquet(buffer, index=False)

    s3 = boto3.client("s3")

    bucket_name = "techchallenge-02-gabriel"

    s3.put_object(Bucket=bucket_name, Key=file_name, Body=buffer.getvalue())

    return {"statusCode": 200, "body": f"Arquivo salvo com sucesso em {file_name}"}


if __name__ == "__main__":
    lambda_handler(None, None)
