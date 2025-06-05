
import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta
import pytz
import numpy as np
import matplotlib.pyplot as plt
from telegram_alerts import send_telegram_alert
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Crypto Signals: Active & Strategic", layout="centered")
st.title("📈 Crypto Signal Dashboard (BTC, ETH, SOL)")

st_autorefresh(interval=1800000, key="data_refresh")

@st.cache_data(ttl=900)
def fetch_data(asset_id):
    url = f"https://api.coingecko.com/api/v3/coins/{asset_id}/market_chart?vs_currency=usd&days=90"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()["prices"]
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except:
        return pd.DataFrame()

def add_indicators(df):
    df["MA30"] = df["price"].rolling(30).mean()
    df["MA100"] = df["price"].rolling(100).mean()
    df["MA200"] = df["price"].rolling(200).mean()
    delta = df["price"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def get_multi_rsi(df):
    daily = df["RSI"].iloc[-1]
    three_day = df["RSI"].rolling(3).mean().iloc[-1]
    weekly = df["RSI"].rolling(7).mean().iloc[-1]
    return daily, three_day, weekly

def load_previous(path="last_signal.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_current(signals, path="last_signal.json"):
    with open(path, "w") as f:
        json.dump(signals, f)

def log_signal(asset, mode, signal, price, rsi, file="signal_log.csv"):
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "asset": asset,
        "mode": mode,
        "signal": signal,
        "price": price,
        "RSI": rsi
    }
    df = pd.DataFrame([row])
    if os.path.exists(file):
        df.to_csv(file, mode="a", header=False, index=False)
    else:
        df.to_csv(file, index=False)

assets = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}
signals_prev = load_previous()
signals_now = {}
signal_msg = []

tz = pytz.timezone("Europe/Stockholm")
now = datetime.now(tz)
clock = now.strftime("%H:%M")

silent = st.checkbox("🔕 Silent Mode (no Telegram alerts)", value=False)
test_btn = st.button("📩 Send Test Alert")

for cid, sym in assets.items():
    st.header(f"{sym}")
    df = fetch_data(cid)
    if df.empty:
        st.warning("No data available.")
        continue
    df = add_indicators(df)
    price = df["price"].iloc[-1]
    rsi = df["RSI"].iloc[-1]
    ma = df["MA30"].iloc[-1]
    ma100 = df["MA100"].iloc[-1]
    ma200 = df["MA200"].iloc[-1]
    rsi_d, rsi_3d, rsi_w = get_multi_rsi(df)

    st.metric("Price", f"${price:,.2f}")
    st.metric("RSI (1D)", f"{rsi_d:.1f}")
    st.metric("MA100", f"${ma100:,.2f}")
    st.metric("MA200", f"${ma200:,.2f}")

    ### Active Signal
    act = "HOLD"
    if rsi < 35 and price < ma:
        act = "BUY"
    elif rsi > 70 and price > ma:
        act = "SELL"

    ### Strategic Signal
    strat = "HOLD"
    score = 0
    if rsi_d < 45: score += 1
    if rsi_3d < 50: score += 1
    if rsi_w < 55: score += 1
    if price > ma100: score += 1
    if price > ma200: score += 1
    if score >= 4:
        strat = "BUY"
    elif score <= 1:
        strat = "SELL"

    conf = int(score / 5 * 100)
    st.markdown(f"**Active Signal**: `{act}`")
    st.markdown(f"**Strategic Signal**: `{strat}` | Confidence: `{conf}%`")

    signals_now[sym] = {"active": act, "strategic": strat}
    log_signal(sym, "active", act, price, rsi)
    log_signal(sym, "strategic", strat, price, rsi)

    if clock == "09:00" or signals_prev.get(sym, {}).get("strategic") != strat:
        signal_msg.append(f"{sym}: {strat} (Conf: {conf}%, Price: ${price:,.2f})")

if (signal_msg or test_btn) and not silent:
    if test_btn:
        msg = "📩 Test Alert:\n" + "\n".join(
            [f"{k}: {v['strategic']}" for k, v in signals_now.items()])
    else:
        msg = "\n".join(signal_msg) + f"\n🕒 {now.strftime('%Y-%m-%d %H:%M')}"
    send_telegram_alert(msg)

save_current(signals_now)

if os.path.exists("signal_log.csv"):
    st.header("📊 Signal History")
    df = pd.read_csv("signal_log.csv")
    for coin in assets.values():
        sub = df[(df["asset"] == coin) & (df["mode"] == "strategic")]
        if not sub.empty:
            fig, ax1 = plt.subplots()
            ax1.plot(pd.to_datetime(sub["timestamp"]), sub["price"], label="Price", color="blue")
            ax2 = ax1.twinx()
            ax2.plot(pd.to_datetime(sub["timestamp"]), sub["RSI"], label="RSI", color="red")
            ax1.set_title(f"{coin} Strategic History")
            st.pyplot(fig)
else:
    st.info("Waiting for signal logs to build.")
