"""Download the 1 minute candle data of stocks over the last 5 years from Polygon S3 bucket."""

import boto3
import os
from botocore.config import Config
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

# Load keys from environment
AWS_ACCESS_KEY = os.environ.get("POLYGON_S3_KEY")
AWS_SECRET_KEY = os.environ.get("POLYGON_S3_SECRET")

# S3 info
bucket_name = "flatfiles"
endpoint_url = "https://files.polygon.io"
prefix = "us_stocks_sip/minute_aggs_v1/"
local_download_path = "./data/minute_bars"

# Create output dir
os.makedirs(local_download_path, exist_ok=True)

# Connect to S3
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    endpoint_url=endpoint_url,
    config=Config(signature_version="s3v4"),
)

# Set cutoff date to 5 years ago
cutoff_date = datetime.today() - timedelta(days=5*365)

# Paginate through all available objects
paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

print("Scanning and downloading available files from the last 5 years...")

for page in pages:
    for obj in page.get("Contents", []):
        key = obj["Key"]
        
        if not key.endswith(".csv.gz"):
            continue

        filename = os.path.basename(key)
        try:
            file_date = datetime.strptime(filename[:10], "%Y-%m-%d")
        except ValueError:
            print(f"Skipping unexpected file name: {filename}")
            continue

        if file_date < cutoff_date:
            continue

        local_file = os.path.join(local_download_path, filename)
        if os.path.exists(local_file):
            print(f"Already downloaded: {filename}")
            continue

        try:
            print(f"Downloading: {filename}")
            s3.download_file(bucket_name, key, local_file)
        except ClientError as e:
            code = e.response["Error"]["Code"]
            print(f"Failed to download {filename}: {code}")
