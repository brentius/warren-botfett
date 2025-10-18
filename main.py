from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import backtrader as bt

from data import fetch_historical_data, parse, fetch_live_data
from strategy import HiddenMarkov, placeholder

#TO GO LIVE - SET ALL TO FALSE
paper = True
backtest = True

load_dotenv()
api_key = os.getenv("alpaca_paper_key" if paper == True else "alpaca_live_key")
api_secret = os.getenv("alpaca_paper_secret" if paper == True else "alpaca_live_secret")

tradeclient = TradingClient(api_key, api_secret, paper = paper)
dataclient = StockHistoricalDataClient(api_key, api_secret)
liveclient = StockDataStream(api_key, api_secret)   

symbols = ["AAPL"]

historical_data = fetch_historical_data(dataclient, symbols)
live_data = fetch_live_data(dataclient, symbols)
cerebro = bt.Cerebro()

for i, (stock, df) in enumerate(historical_data.items()):
    data_feed = parse(df)
    cerebro.adddata(data_feed, name = stock)
    if i == 0:
        master_feed = data_feed
    else:
        data_feed.plotinfo.plotmaster = master_feed
        data_feed.plotinfo.sameaxis = True

cerebro.addstrategy(placeholder)

if backtest == True:
    print(f"Starting portfolio value: {round(cerebro.broker.getvalue(), 2)}")
    results = cerebro.run()
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.plot()