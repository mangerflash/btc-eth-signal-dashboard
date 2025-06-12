import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(page_title="BTC/ETH Signal Dashboard", layout="wide")
st.title("📊 BTC/ETH Signal Dashboard")

st.markdown("### Signal Overview")

# Fetch data
btc = yf.download("BTC-USD", period="60d", interval="1h")
eth = yf.download("ETH-USD", period="60d", interval="1h")

# Technical indicators
btc['EMA_21'] = ta.ema(btc['Close'], length=21)
eth['EMA_21'] = ta.ema(eth['Close'], length=21)

# Signal logic (simplified)
btc_signal = "BUY" if btc['Close'].iloc[-1] > btc['EMA_21'].iloc[-1] else "SELL"
eth_signal = "BUY" if eth['Close'].iloc[-1] > eth['EMA_21'].iloc[-1] else "SELL"

st.subheader("BTC Signal")
st.info(f"**{btc_signal}** signal based on EMA21")

st.subheader("ETH Signal")
st.info(f"**{eth_signal}** signal based on EMA21")

# Plot charts
def plot_chart(df, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], name='EMA 21'))
    fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Price")
    return fig

st.plotly_chart(plot_chart(btc, "BTC Price & EMA21"), use_container_width=True)
st.plotly_chart(plot_chart(eth, "ETH Price & EMA21"), use_container_width=True)
