import streamlit as st
import pandas as pd
import numpy as np
import datetime
from telegram_alerts import send_message

st.set_page_config(page_title="Crypto Signal Dashboard", layout="wide")

# UI Toggles
st.sidebar.title("Settings")
silent_mode = st.sidebar.toggle("🔕 Silent Mode", value=True)
quiet_hours = st.sidebar.toggle("🌙 Enable Quiet Hours (18:00–08:00)", value=True)
if st.sidebar.button("📤 Send Test Telegram Message"):
    sent = send_message("✅ Test message from Mange's Crypto Dashboard")
    st.sidebar.success("Message sent!" if sent else "Failed to send.")

# Simulated signal data for BTC, ETH, SOL (replace with real logic)
assets = ["BTC", "ETH", "SOL"]
now = datetime.datetime.now()
hour = now.hour

for asset in assets:
    st.markdown(f"## {asset} Overview")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Short-Term", "BUY" if asset == "BTC" else "HOLD")
    with col2:
        st.metric("Strategic", "HOLD" if asset != "SOL" else "SELL")
    with col3:
        st.metric("Long-Term", "BUY")

    st.markdown("**Signal Breakdown**")
    st.write({
        "RSI (1D)": 42,
        "MA100": "Above",
        "MA200": "Above",
        "MACD": "Bullish",
        "Support Zone": "$85K",
        "Resistance Zone": "$97.5K"
    })

    st.markdown("**📊 Risk/Reward Gauge**")
    rsi = np.random.randint(30, 70)
    gauge = ["🟩"] * (rsi // 10) + ["⬜"] * (10 - (rsi // 10))
    st.write(f"RSI {rsi}: {''.join(gauge)}")

    st.markdown("**📈 Signal History (Strategic)**")
    df = pd.DataFrame({
        "Date": pd.date_range(end=datetime.date.today(), periods=10),
        "Signal": np.random.choice(["BUY", "HOLD", "SELL"], size=10)
    })
    st.line_chart(df.set_index("Date"))

    # Telegram push logic
    if not silent_mode and (not quiet_hours or (hour >= 8 and hour < 18)):
        send_message(f"📣 {asset}: Signal Update
Short-Term: BUY
Strategic: HOLD
Long-Term: BUY")

st.success("Dashboard loaded successfully.")