from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import os
import backtrader as bt
from data import fetch_historical_data, parse, fetch_live_data
from strategy import test

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

symbols = ["AAPL", "MSFT", "NVDA", "GOOG", "JPM", "BA"] #TRADE THESE

historical_data = fetch_historical_data(dataclient, symbols)
live_data = fetch_live_data(dataclient, symbols)

if backtest == True:
    cerebro = bt.Cerebro()

    for stock, df in historical_data.items():
        data_feed = parse(df)
        cerebro.adddata(data_feed, name = stock)

    cerebro.addstrategy(test) #strategy

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    results = cerebro.run()

    sharpe = results[0].analyzers.sharpe.get_analysis()
    drawdown = results[0].analyzers.drawdown.get_analysis()
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    print(f"Sharpe Ratio: {sharpe['sharperatio']}")
    print(f"Max Drawdown: {drawdown['max']['drawdown']:.2f}%")
    cerebro.plot()

if backtest == False:
    for symbol in symbols: