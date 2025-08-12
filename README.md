# WARREN BOTFETT

A lightweight, modular quantitative trading bot that runs on a Raspberry Pi 5 and uses Alpaca and Backtrader to trade US stocks.

## Features

- Fetches real-time and historical stock data via Alpaca
- Signal + confidence generation with a customisable strategy - just plug and play
- Backtesting engine to simulate portfolio performance
- Ranking system to select top tickers from a watchlist
- Risk management to avoid losing too much capital
- Paper/live trading with Alpaca's broker API

## Structure

There are 6 python files in this repo:
- ```data.py``` fetches historical and live stock data from Alpaca and feeds it into a ```pandas.DataFrame```
- ```strategy.py``` determines whether to buy, sell or hold a stock given a ```pandas.DataFrame``` of price data, and selects the top 3 stocks to trade
- ```broker.py``` places orders with the Alpaca API
- ```risk.py``` enforces rules to protect capital and limit risk per trade
- ```main.py``` ties it all together, and allows you to toggle between paper, backtesting or live trading

## Usage

1. Clone the repository:

```bash
git clone https://github.com/brentius/warren-botfett.git
cd warren-botfett
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your ```.env``` file with Alpaca API keys:

```env
APCA_API_KEY_ID = your_api_key_here
APCA_API_SECRET_KEY = your_secret_key_here
APCA_API_BASE_URL = https://paper-api.alpaca.markets
```

4. Run it! To backtest a strategy:

```bash
python backtest.py
```

To fetch data and check signals:

```bash
python strategy.py
```

## Requirements:
- Alpaca API keys (```alpaca.markets```)
- Python 3.x or above

## Todo

- [ ] Improve strategy optimization with machine learning
- [ ] Add forex trading