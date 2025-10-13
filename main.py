from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
from data import fetch_historical_data, parse, fetch_live_data
from strategy import HiddenMarkov

#TO GO LIVE - SET ALL TO FALSE
paper = True
backtest = True

load_dotenv()
api_key = os.getenv("alpaca_paper_key" if paper == True else "alpaca_live_key")
api_secret = os.getenv("alpaca_paper_secret" if paper == True else "alpaca_live_secret")
base_url = os.getenv("alpaca_base_url")

tradeclient = TradingClient(api_key, api_secret, paper = paper)
dataclient = StockHistoricalDataClient(api_key, api_secret)
liveclient = StockDataStream(api_key, api_secret)   

symbols = ["AAPL", "TSLA"]
    
historical_data = fetch_historical_data(dataclient, symbols)
live_data = fetch_live_data(dataclient, symbols)

for stock, df in historical_data.items():
    model, states, data = HiddenMarkov(df)

    fig, ax = plt.subplots()
    ax.plot(model.means_[states], ".-", ms=6, mfc="orange")
    ax.plot(data)
    ax.set_title(f'{stock}')
    ax.set_xlabel('State')
    plt.show()