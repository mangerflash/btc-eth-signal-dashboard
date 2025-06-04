
import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime
from telegram_alerts import send_telegram_alert

st.set_page_config(page_title="BTC, ETH & SOL Signal Dashboard", layout="centered")
st.title("📈 Multi-Asset Crypto Signal Dashboard")

def fetch_price_data(asset_id):
    url = f"https://api.coingecko.com/api/v3/coins/{asset_id}/market_chart?vs_currency=usd&days=90"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            st.error(f"❌ API error {r.status_code} for {asset_id}")
            return pd.DataFrame()
        response = r.json()
        if "prices" not in response:
            st.error(f"❌ 'prices' key missing in API response for {asset_id}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Failed to fetch data for {asset_id}: {e}")
        return pd.DataFrame()

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

def load_previous_signals(path="last_signal.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_current_signals(signals, path="last_signal.json"):
    with open(path, "w") as f:
        json.dump(signals, f)

def log_signal(asset, signal, price, rsi, reason, log_file="signal_log.csv"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = pd.DataFrame([{
        "timestamp": timestamp,
        "asset": asset,
        "signal": signal,
        "price": price,
        "RSI": rsi,
        "reason": reason
    }])
    if os.path.exists(log_file):
        entry.to_csv(log_file, mode='a', header=False, index=False)
    else:
        entry.to_csv(log_file, index=False)

assets = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL"
}

prev_signals = load_previous_signals()
current_signals = {}
signal_messages = []
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
hour_minute = datetime.now().strftime("%H:%M")

for asset_id, symbol in assets.items():
    st.header(symbol)
    df = fetch_price_data(asset_id)
    if df.empty:
        continue
    df = calculate_indicators(df)

    price = df["price"].iloc[-1]
    rsi = df["RSI"].iloc[-1]
    ma = df["MA30"].iloc[-1]

    st.metric("Current Price", f"${price:,.2f}")
    st.metric("RSI", f"{rsi:.2f}")
    st.metric("30D MA", f"${ma:,.2f}")

    signal = "HOLD"
    reason = "Neutral range"
    if rsi < 35 and price < ma:
        signal = "BUY"
        reason = "RSI < 35 and price below MA30"
    elif rsi > 70 and price > ma:
        signal = "SELL"
        reason = "RSI > 70 and price above MA30"

    st.subheader(f"📍 Signal: {signal}")
    current_signals[symbol] = signal
    log_signal(symbol, signal, price, rsi, reason)

    if hour_minute == "09:00" or prev_signals.get(symbol) != signal:
        signal_messages.append(f"{symbol}: {signal} (Price: ${price:,.2f}, RSI: {rsi:.2f})")

# Send alert if needed
if signal_messages:
    message = "\n".join(signal_messages)
    message += f"\n\n🕒 Refreshed at {timestamp}"
    send_telegram_alert(message)

# Save state
save_current_signals(current_signals)

# Preview alert
if signal_messages:
    st.subheader("📩 Telegram Message Preview")
    st.text(message)
else:
    st.info("No new signal change. No Telegram alert sent.")
