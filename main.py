from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import backtrader as bt
import numpy as np

from data import fetch_historical_data, parse, fetch_live_data
from strategy import HiddenMarkov

#TO GO LIVE - SET ALL TO FALSE
paper = True
backtest = True

load_dotenv()
api_key = os.getenv("alpaca_paper_key" if paper == True else "alpaca_live_key")
api_secret = os.getenv("alpaca_paper_secret" if paper == True else "alpaca_live_secret")

tradeclient = TradingClient(api_key, api_secret, paper = paper)
dataclient = StockHistoricalDataClient(api_key, api_secret)
liveclient = StockDataStream(api_key, api_secret)   

symbols = ["MSFT"]

historical_data = fetch_historical_data(dataclient, symbols) #change to CSV when final implementation
live_data = fetch_live_data(dataclient, symbols)
cerebro = bt.Cerebro()

def plot_states(price, states):
    plt.figure(figsize=(14,6))

    # Plot the price
    plt.plot(price, label="Price", linewidth=1.3)

    # Overlay states (each state gets its own color band)
    for state in np.unique(states):
        mask = states == state
        plt.scatter(
            np.arange(len(price))[mask],
            price[mask],
            s=10,
            label=f"State {state}"
        )

    plt.title("Price vs Hidden Markov States")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()

for symbol, df in historical_data.items():
    model, states, data = HiddenMarkov(df)
    price = df["close"].to_numpy()
    plot_states(price[1:], states)