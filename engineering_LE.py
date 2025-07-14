import pandas as pd
import numpy as np

"""Here we are defining and putting logic for phase 1 of consolidation starting with Buying climax/ exhaustion"""

# Re-define and apply the function using user's logic
def find_automatic_reaction_end(df, peak_index, rebound_ratio=0.4, max_lookahead=40):
    peak_price = df.loc[peak_index, "high"]
    lowest_low = np.inf
    lowest_index = None
    end_index = None

    for i in range(peak_index + 1, min(len(df), peak_index + max_lookahead)):
        current_low = df.loc[i, "low"]
        current_close = df.loc[i, "close"]

        if current_low < lowest_low:
            lowest_low = current_low
            lowest_index = i

        drop = peak_price - lowest_low

        if drop > 0 and current_close >= lowest_low + rebound_ratio * drop:
            ar_low = df.loc[peak_index + 1:i, "low"].min()
            ar_low_index = df.loc[peak_index + 1:i, "low"].idxmin()
            end_index = i
            return end_index, ar_low, ar_low_index, lowest_index

    return None, None, None, None

def find_secondary_test_high(df, ar_low_index, drop_ratio=0.4, max_lookahead=40):
    ar_low_price = df.loc[ar_low_index, "low"]
    highest_high = ar_low_price
    highest_index = ar_low_index

    for i in range(ar_low_index + 1, min(len(df), ar_low_index + max_lookahead)):
        current_high = df.loc[i, "high"]
        current_close = df.loc[i, "close"]

        if current_high > highest_high:
            highest_high = current_high
            highest_index = i

        rise = highest_high - ar_low_price
        if rise > 0 and current_close <= highest_high - drop_ratio * rise:
            return highest_index

    return None

def detect_buying_climax(stock_df, lookback=250):
    stock_df = stock_df.reset_index(drop=True)
    stock_df["buying_climax_or_exhaustion"] = 0
    stock_df["auto_reaction_low"] = 0
    stock_df["secondary_test_high"] = 0

    i = 3
    while i < len(stock_df) - 8:
        peak_high = stock_df.loc[i, "high"]

        is_local_peak = all(stock_df.loc[i - j, "high"] < peak_high for j in range(1, 4)) and \
                        all(stock_df.loc[i + j, "high"] < peak_high for j in range(1, 4))

        if not is_local_peak:
            i += 1
            continue

        recent_highs = stock_df.loc[max(0, i - lookback):i - 1, "high"]
        if any(peak_high <= recent_highs):
            i += 1
            continue

        ar_end_index, ar_low, ar_low_index, lowest_index = find_automatic_reaction_end(stock_df, i)

        if ar_end_index is not None:
            st_high_index = find_secondary_test_high(stock_df, ar_low_index)
            if st_high_index is not None and stock_df.loc[st_high_index, "close"] <= peak_high:
                stock_df.loc[i, "buying_climax_or_exhaustion"] = 1
                stock_df.loc[ar_low_index, "auto_reaction_low"] = 1
                stock_df.loc[st_high_index, "secondary_test_high"] = 1
                i = st_high_index + 1
                continue

        i += 1

    return stock_df

# Apply to your DataFrame
stock_df = detect_buying_climax(stock_df)





'''Vis
# Ensure datetime is parsed and set as index
stock_df['datetime'] = pd.to_datetime(stock_df['window_start'])
stock_df.set_index('datetime', inplace=True)

# Filter for a specific 1-day period
start_date = "2024-07-11"
end_date = "2024-07-11"  # next day (exclusive)
filtered_df = stock_df.loc[start_date:end_date]

# OHLC data
ohlc = filtered_df[['open', 'high', 'low', 'close']]

# Marker data for climax points
buying_climax_exh_marker = np.where(
    filtered_df['buying_climax_or_exhaustion'] == 1,
    filtered_df['high'],
    np.nan
)

auto_reaction_low_marker = np.where(
    filtered_df['auto_reaction_low'] == 1,
    filtered_df['low'],
    np.nan
)

st_high_marker = np.where(
    filtered_df['secondary_test_high'] == 1,
    filtered_df['high'],
    np.nan
)

# Create scatter addplot
climax_exh_markers = mpf.make_addplot(
    buying_climax_exh_marker,
    type='scatter',
    markersize=100,
    marker='v',
    color='red'
)

marker_y = auto_reaction_low_marker - 0  # tweak 0.5 as needed

# Create scatter addplot
auto_reaction_low_markers = mpf.make_addplot(
    marker_y,
    type='scatter',
    markersize=70,
    marker='^',
    color='blue'
)

# Create scatter addplot
secondary_test_high = mpf.make_addplot(
    st_high_marker,
    type='scatter',
    markersize=70,
    marker='o',
    color='black'
)

# Plot the candlestick chart with markers
mpf.plot(
    ohlc,
    type='candle',
    style='charles',
    title='Candlestick Chart with Buying Climax Markers (June 3, 2024)',
    ylabel='Price',
    figratio=(16, 9),
    figscale=1.5,
    addplot=[climax_exh_markers, auto_reaction_low_markers, secondary_test_high]
)ualizing the data'''
