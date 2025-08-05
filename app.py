import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import pandas_ta as ta

st.set_page_config(page_title="BTC & ETH Signal Dashboard", layout="wide")

# Fetch data
@st.cache_data
def load_data(ticker):
    df = yf.download(ticker, period="6mo", interval="1d")
    df["RSI"] = ta.rsi(df["Close"])
    df["MACD"] = ta.macd(df["Close"])["MACD_12_26_9"]
    df["Signal"] = ta.macd(df["Close"])["MACDs_12_26_9"]
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()
    return df

st.title("📊 BTC & ETH Signal Dashboard")

asset = st.selectbox("Select asset:", ["BTC-USD", "ETH-USD"])
df = load_data(asset)

# Plot price chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="MA50"))
fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], name="MA200"))
fig.update_layout(title=f"{asset} Price Chart", height=400)
st.plotly_chart(fig, use_container_width=True)

# Signal logic
def get_signal(row):
    if row["RSI"] < 30 and row["Close"] > row["MA50"] > row["MA200"]:
        return "BUY"
    elif row["RSI"] > 70 and row["Close"] < row["MA50"] < row["MA200"]:
        return "SELL"
    return "HOLD"

df["Signal_Type"] = df.apply(get_signal, axis=1)

st.subheader("Latest Signal")
st.metric(label="Signal", value=df["Signal_Type"].iloc[-1])

st.subheader("RSI & MACD")
st.dataframe(df[["RSI", "MACD", "Signal"]].tail(10))