
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Crypto Signal Debug View", layout="centered")

st.title("🧪 Debug Mode: BTC & ETH Signal Dashboard")

def fetch_price_data(asset_id):
    url = f"https://api.coingecko.com/api/v3/coins/{asset_id}/market_chart?vs_currency=usd&days=90"
    response = requests.get(url).json()
    prices = response["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df["price"] = df["price"].astype(float)
    return df

def calculate_indicators(df):
    df["MA30"] = df["price"].rolling(window=30).mean()
    delta = df["price"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

assets = ["bitcoin", "ethereum"]

for asset in assets:
    st.header(asset.upper())
    df = fetch_price_data(asset)
    df = calculate_indicators(df)

    latest_rsi = df["RSI"].iloc[-1]
    latest_price = df["price"].iloc[-1]
    ma = df["MA30"].iloc[-1]

    st.metric(label="Current Price", value=f"${latest_price:,.2f}")
    st.metric(label="RSI", value=f"{latest_rsi:.2f}")
    st.metric(label="30D MA", value=f"${ma:,.2f}")

    signal = "HOLD"
    if latest_rsi < 35 and latest_price < ma:
        signal = "BUY"
    elif latest_rsi > 70 and latest_price > ma:
        signal = "SELL"

    st.subheader(f"📍 Signal: {signal}")
    st.text(f"Price: ${latest_price:,.2f}, RSI: {latest_rsi:.2f}, MA30: ${ma:,.2f}")
