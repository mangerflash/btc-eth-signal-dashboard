import streamlit as st
import time

# Auto-refresh every 30 minutes
st.experimental_rerun_timer = st.empty()
time.sleep(1800)  # 1800 seconds = 30 minutes
st.experimental_rerun()

import streamlit as st
import pandas as pd
import datetime
from indicators import fetch_price_data, calculate_indicators
from telegram_alerts import send_telegram_alert

st.set_page_config(page_title="BTC & ETH Signal Dashboard", layout="wide")

st.title("📈 Bitcoin & Ethereum Signal Dashboard")

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

    # Signal logic
    signal = "HOLD"
    if latest_rsi < 35 and latest_price < ma:
        signal = "BUY"
    elif latest_rsi > 70 and latest_price > ma:
        signal = "SELL"

    st.subheader(f"📍 Signal: {signal}")
    signal_messages.append(f"{asset.upper()}: {signal} (Price: ${latest_price:,.2f}, RSI: {latest_rsi:.2f})")

# Send Telegram Alert
alert_message = "\n".join(signal_messages)
send_telegram_alert(alert_message)
