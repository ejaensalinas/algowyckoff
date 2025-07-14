"""Feature engineering script"""

import pandas as pd
import numpy as np

df = pd.read_csv("/Users/esalinas/Desktop/base_data.csv", parse_dates=["window_start"])
df.sort_values(["ticker", "window_start"], inplace=True)

df["window_start"] = pd.to_datetime(
    df["window_start"].astype(np.int64), unit="ns", utc=True
)
df["window_start"] = df["window_start"].dt.tz_convert("US/Central")
df["close_pct"] = (df["close"] - df["open"]) / df["open"]
df["high_pct"] = (df["high"] - df["open"]) / df["open"]
df["low_pct"] = (df["low"] - df["open"]) / df["open"]
df["body_pct"] = (df["close"] - df["open"]) / df["open"]
df["upper_wick_pct"] = (df["high"] - df[["close", "open"]].max(axis=1)) / df["open"]
df["lower_wick_pct"] = (df[["close", "open"]].min(axis=1) - df["low"]) / df["open"]

# Using these fields to remove data form outside of trading hours
df["hour"] = df["window_start"].dt.hour
df["minute"] = df["window_start"].dt.minute

# Keep rows where time is between 8:30 AM and 3:00 PM CT
df_market = df[(df["hour"] > 8) | ((df["hour"] == 8) & (df["minute"] >= 30))]
df_market = df_market[
    (df_market["hour"] < 15) | ((df_market["hour"] == 15) & (df_market["minute"] == 0))
]

# Drop helper columns
df_market = df_market.drop(columns=["hour", "minute"])

# Z-score
df["volume_zscore"] = (df["volume"] - df["volume"].rolling(100).mean()) / df[
    "volume"
].rolling(100).std()

# Relative volume (optional, also helpful)
df["volume_rel"] = df["volume"] / df["volume"].rolling(100).mean()
