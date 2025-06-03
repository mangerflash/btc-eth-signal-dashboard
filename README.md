
# BTC & ETH Signal Dashboard

This dashboard analyzes Bitcoin and Ethereum price data to generate simple investment signals (BUY / SELL / HOLD) based on RSI and moving average.

## Features
- Live price feed from CoinGecko
- Technical indicator calculations (RSI, 30-day MA)
- Streamlit-based web interface
- Telegram notifications for signal alerts

## Setup
1. Add your Telegram bot token and chat ID in `telegram_alerts.py`
2. Run the app:
```bash
streamlit run app.py
```

Or deploy via Streamlit Cloud.

## To Do
- Integrate on-chain analytics
- Add sentiment analysis
- Backtesting engine
