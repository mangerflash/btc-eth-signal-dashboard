
import streamlit as st
import pandas as pd
import requests
from telegram_alerts import send_telegram_alert
from datetime import datetime

st.set_page_config(page_title="BTC & ETH Signal Dashboard", layout="centered")

st.title("📈 BTC & ETH Signal Dashboard")

def fetch_price_data(asset_id):
    url = f"https://api.coingecko.com/api/v3/coins/{asset_id}/market_chart?vs_currency=usd&days=90"
    response = requests.get(url).json()
if "prices" not in response:
    st.error(f"❌ Failed to load data for {asset_id.title()}")
    return pd.DataFrame()  # return empty DataFrame

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
signal_messages = []

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
    signal_messages.append(f"{asset.upper()}: {signal} (Price: ${latest_price:,.2f}, RSI: {latest_rsi:.2f})")

# Add timestamp to force Telegram delivery
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
alert_message = "\n".join(signal_messages)
alert_message += f"\n\n🕒 Refreshed at {timestamp}"

send_telegram_alert(alert_message)

# Preview alert content
st.subheader("📩 Telegram Message Preview")
st.text(alert_message)
