# WARREN BOTFETT

A lightweight, modular quantitative trading bot that runs on a Raspberry Pi 5 and uses Alpaca and Backtrader to trade US stocks.

## Features

- Fetches real-time and historical stock data via Alpaca
- Signal + confidence generation with a customisable strategy - just plug and play
- Backtesting engine to simulate portfolio performance with backtrader
- Ranking system to select top tickers from a watchlist
- Risk management to avoid losing too much capital
- Paper/live trading with Alpaca's broker API

## Structure

There are 3 main python files in this repo:
- ```data.py``` fetches historical and live stock data from Alpaca and feeds it into a ```pandas.DataFrame```
- ```strategy.py``` determines whether to buy, sell or hold a stock given a ```pandas.DataFrame``` of price data, and selects the top 3 stocks to trade
- ```main.py``` ties it all together, and allows you to toggle between paper, backtesting or live trading - it also allows you to place orders with the Alpaca API, and utilise backtesting. If you want to do just about anything with this repo, this is where you control stuff.

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

3. Set up your ```.env``` file with Alpaca API keys, taken from ```alpaca.markets```:

```env
alpaca_paper_key = paper_key_here
alpaca_paper_secret = paper_secret_here
alpaca_live_key = live_key_here
alpaca_live_secret = live_secret_here
```

4. Run it! To backtest a strategy:

```bash
backtest = True
python main.py
```

To fetch data and check signals:

```bash
python strategy.py
```

## Requirements:
- Alpaca API keys (```alpaca.markets```)
- Python 3.x or above

## To do:
- [ ] Stochastic calculus for position sizing and buy/hold/sell signals - stocks will be selected via confidence