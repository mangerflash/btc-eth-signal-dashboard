import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="BTC/ETH Signal Dashboard", layout="wide")
st.title("📊 BTC/ETH Signal Dashboard")

st.markdown("### Signal Overview")
st.info("Signals are generated based on technical indicators, macro conditions, and risk models.")

tickers = ['BTC-USD', 'ETH-USD']
data = {ticker: yf.download(ticker, period='90d', interval='1d') for ticker in tickers}

for ticker, df in data.items():
    df['RSI'] = ta.rsi(df['Close'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', yaxis='y2'))
    fig.update_layout(
        title=f"{ticker} Price & RSI",
        yaxis2=dict(overlaying='y', side='right', range=[0, 100]),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)