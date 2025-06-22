# WARREN BOTFETT

A lightweight, modular quantitative trading bot that runs on a Raspberry Pi 5 and uses Alpaca to trade US stocks.

## Features

- Fetches real-time and historical stock data via Alpaca
- Signal generation with customisable trading strategies
- Backtesting engine to simulate portfolio performance
- Ranking system to select top tickers from a watchlist and to replace the bottom tickers
- Risk management to avoid losing too much capital
- Paper/live trading with Alpaca's broker API

## Structure

There are 7 python files in this repo (discounting ```main.py```):
- ```data.py``` fetches historical and live stock data from Alpaca and feeds it into a ```pandas.DataFrame```
- ```strategy.py``` determines whether to buy, sell or hold a stock given a ```pandas.DataFrame``` of price data
- ```backtest.py``` runs the strategy on historical data to simulate portfolio performance
- ```ranking.py``` decides which stocks out of a list are most promising to trade and swaps out the worst-performing stocks
- ```broker.py``` places orders with the Alpaca API
- ```risk.py``` enforces rules to protect capital and limit risk per trade
- ```logger.py``` tracks all trades, signals, errors, and performance for later review

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
APCA_API_KEY_ID=your_api_key_here
APCA_API_SECRET_KEY=your_secret_key_here
APCA_API_BASE_URL=https://paper-api.alpaca.markets
```

4. Run it! To backtest a strategy:

```bash
python backtest.py
```

To fetch data and check signals:

```bash
python strategy.py
```

## Todo

- [ ] Add a web UI for dataview of stocks
- [ ] Add email alerts for trades
- [ ] Improve strategy optimization with machine learning