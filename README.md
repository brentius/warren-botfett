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

## TODO

- [ ] Add a web UI for dataview of stocks
- [ ] Add email alerts for trades
- [ ] Improve strategy optimization with machine learning