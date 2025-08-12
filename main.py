from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from dotenv import load_dotenv
import os
import argparse
import backtrader as bt
import backtrader.feeds as btfeeds
import pandas as pd
from data import fetch_historical_data, fetch_live_data
from strategy import placeholder

#TO GO LIVE - SET BOTH TO FALSE
paper = True
backtest = True

load_dotenv()
api_key = os.getenv("alpaca_paper_key" if paper == True else "alpaca_live_key")
api_secret = os.getenv("alpaca_paper_secret" if paper == True else "alpaca_live_secret")
base_url = os.getenv("alpaca_base_url")

tradeclient = TradingClient(api_key, api_secret, paper = paper)
dataclient = StockHistoricalDataClient(api_key, api_secret)
liveclient = StockDataStream(api_key, api_secret)

symbols = ["AAPL", "MSFT", "NVDA", "GOOG"] #TRADE THESE

historical_data = fetch_historical_data(dataclient, symbols)
live_data = fetch_live_data(dataclient, symbols)

def parse_to_bt(df, datetime_col=None):
    df_copy = df.copy()

    if datetime_col:
        df_copy[datetime_col] = pd.to_datetime(df_copy[datetime_col])
        df_copy.set_index(datetime_col, inplace=True)
    else:
        if not pd.api.types.is_datetime64_any_dtype(df_copy.index):
            raise ValueError("DataFrame index must be datetime or specify datetime_col parameter.")
    df_copy.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)
    df_copy = df_copy[['Open', 'High', 'Low', 'Close', 'Volume']]
    return bt.feeds.PandasData(dataname = df_copy)

cerebro = bt.Cerebro()

for stock, df in historical_data.items():
    data_feed = parse_to_bt(df)
    cerebro.adddata(data_feed, name = stock)

# Add your strategy here
cerebro.addstrategy(placeholder)

cerebro.run()
cerebro.plot()