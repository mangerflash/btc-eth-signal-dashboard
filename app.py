import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas_ta as ta

# --------- Settings ----------
ASSETS = ['BTC-USD', 'ETH-USD']
QUIET_HOURS_START = 18  # 18:00
QUIET_HOURS_END = 8     # 08:00

# --------- App Config ---------
st.set_page_config(page_title="BTC/ETH Signal Dashboard", layout="wide")
st.title("📈 BTC & ETH Signal Dashboard")

# --------- Functions ----------
def is_quiet_hours():
    now = datetime.now().hour
    return QUIET_HOURS_START <= now or now < QUIET_HOURS_END

def fetch_data(ticker, days=90):
    end = datetime.now()
    start = end - timedelta(days=days)
    return yf.download(ticker, start=start, end=end)

def generate_signals(df):
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['MACD'] = ta.macd(df['Close']).iloc[:,0]

    # Short-Term: EMA20 vs EMA50
    short_signal = 'BUY' if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] else 'SELL'

    # Strategic: RSI
    rsi_val = df['RSI'].iloc[-1]
    if rsi_val < 35:
        strat_signal = 'BUY'
    elif rsi_val > 65:
        strat_signal = 'SELL'
    else:
        strat_signal = 'HOLD'

    # Long-Term: MACD direction
    macd_val = df['MACD'].iloc[-1]
    prev_macd_val = df['MACD'].iloc[-2]
    long_signal = 'BUY' if macd_val > prev_macd_val else 'SELL'

    return short_signal, strat_signal, long_signal

def plot_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], mode='lines', name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], mode='lines', name='EMA50'))
    fig.update_layout(title=f'{ticker} Price Chart', xaxis_title='Date', yaxis_title='Price')
    return fig

# --------- UI Controls ---------
silent_mode = st.sidebar.toggle("🔕 Silent Mode", value=is_quiet_hours())

# --------- Main Dashboard ---------
for asset in ASSETS:
    st.subheader(asset)
    df = fetch_data(asset)

    short, strat, long = generate_signals(df)

    cols = st.columns(3)
    cols[0].metric("📉 Short-Term Signal", short)
    cols[1].metric("📊 Strategic Signal", strat)
    cols[2].metric("📈 Long-Term Signal", long)

    with st.expander(f"📊 Chart & Analysis for {asset}"):
        st.plotly_chart(plot_chart(df, asset), use_container_width=True)
        st.write("🧠 **Signal Logic Breakdown**")
        st.markdown(f"""
        - **Short-Term**: EMA20 vs EMA50 → `{short}`
        - **Strategic**: RSI (current {df['RSI'].iloc[-1]:.2f}) → `{strat}`
        - **Long-Term**: MACD trend → `{long}`
        """)

# --------- Telegram Push (disabled in UI preview) ---------
if not silent_mode:
    st.success("📬 Push notification *would* be sent now (if enabled)")
