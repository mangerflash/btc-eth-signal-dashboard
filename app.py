
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import plotly.graph_objs as go

st.set_page_config(layout="wide", page_title="Multi-Horizon Crypto Signal Dashboard")

# --- Parameters ---
assets = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana"
}

quiet_hours = st.sidebar.toggle("🔕 Quiet Hours Mode (18:00–08:00)", value=True)
now_hour = dt.datetime.now().hour
is_quiet = quiet_hours and (now_hour < 8 or now_hour >= 18)

timeframes = {
    "Short-Term": 7,
    "Strategic": 30,
    "Long-Term": 90
}

# --- Helper Functions ---
def fetch_data(ticker, period="180d"):
    df = yf.download(ticker, period=period, interval="1d")
    df.dropna(inplace=True)
    df["MA30"] = df["Close"].rolling(window=30).mean()
    df["MA90"] = df["Close"].rolling(window=90).mean()
    df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().add(1).rolling(14).apply(
        lambda x: np.mean(x[x > 0]) / np.mean(-x[x < 0]) if np.mean(-x[x < 0]) != 0 else 0, raw=False)))
    df["Signal"] = np.where(df["Close"] > df["MA30"], "BUY", "SELL")
    return df

def evaluate_macro_factors():
    war = "🟧 Geopolitical tension (neutral)"
    inflation = "🟩 Inflation cooling (positive)"
    liquidity = "🟥 Liquidity tightening (negative)"
    return [war, inflation, liquidity]

def signal_breakdown(df):
    last = df.iloc[-1]
    rsi = last["RSI"]
    ma30 = last["MA30"]
    close = last["Close"]
    risk = "🔥 High Risk" if rsi > 70 else "⚠️ Moderate" if rsi > 50 else "🟢 Low Risk"
    reward = "📈 High Potential" if close > ma30 else "📉 Weak Momentum"
    return risk, reward

# --- App Layout ---
st.title("📊 Multi-Horizon Crypto Signal Dashboard")

for ticker, name in assets.items():
    st.header(name)
    df = fetch_data(ticker)
    if df.empty:
        st.error("Failed to fetch data.")
        continue

    col1, col2 = st.columns([1, 3])
    with col1:
        for label, days in timeframes.items():
            change = df["Close"].iloc[-1] - df["Close"].iloc[-days]
            direction = "🔺 Buy" if change > 0 else "🔻 Sell"
            st.metric(label, value=f"${df['Close'].iloc[-1]:,.2f}", delta=direction)

        risk, reward = signal_breakdown(df)
        st.markdown(f"**Risk Level:** {risk}")
        st.markdown(f"**Reward Outlook:** {reward}")

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=df.index, y=df["MA30"], name="MA30", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=df.index, y=df["MA90"], name="MA90", line=dict(color="green")))
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 Strategic Signal Breakdown"):
        for macro in evaluate_macro_factors():
            st.markdown(f"- {macro}")
        st.line_chart(df[["Close", "MA30", "MA90"]])

if not is_quiet:
    st.success("✅ Signal logic processed. Notifications allowed.")
else:
    st.info("🔕 Quiet Hours active. No alerts dispatched.")
