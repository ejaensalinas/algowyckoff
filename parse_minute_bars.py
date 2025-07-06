"""Parsing and unionizing 1 minute bar data files"""
import os
import gzip
import pandas as pd

# Path to your local data
data_dir = os.path.expanduser("~/Desktop/data/minute_bars")
target_tickers = {
    "AAPL",
    "TSLA",
    "META",
    "VLO",
    "PCAR",
    "GE",
    "MERK",
    "LLY",
    "UNH",
    "CTAS",
    "CPRT",
    "SBH",
    "AAP",
    "TGTX",
}

all_dfs = []

for file_name in sorted(os.listdir(data_dir)):
    if file_name.endswith(".csv.gz"):
        file_path = os.path.join(data_dir, file_name)
        with gzip.open(file_path, "rt") as f:
            df = pd.read_csv(f)
            df_filtered = df[df["ticker"].isin(target_tickers)]
            all_dfs.append(df_filtered)

# Combine all
base_data = pd.concat(all_dfs, ignore_index=True)

# Save to CSV or Parquet
base_data.to_csv("base_data.csv", index=False)
print("Parsed and saved to base_data.csv")
