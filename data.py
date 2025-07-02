#data.py
#scrape + clean price data

#imports
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import StockDataStream
import asyncio
from dotenv import load_dotenv
import os

#load api keys
load_dotenv()
api_key = os.getenv("APCA_API_KEY_ID")
api_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

#create client - connect to alpaca
dataclient = StockHistoricalDataClient(api_key, api_secret)

#fetch historical bars + clean
def historical_fetch(symbols, timeframe = TimeFrame.Day, start = "2025-01-01"):
    request = StockBarsRequest(
        symbol_or_symbols = symbols,
        start = start,
        timeframe = timeframe
    )
    raw_history = dataclient.get_stock_bars(request).df
    def clean_data(raw_history, symbols):
        history_data = {}
        for symbol in symbols:
            df = raw_history.loc[symbol].copy()
            df.index = pd.to_datetime(df.index)
#            df.index = df.index.tz_localize("UTC").tz_convert("America/New_York")
            df.sort_index(inplace = True)
            df.columns = [col.lower() for col in df.columns]
            df.dropna(subset=['close'], inplace=True)
            history_data[symbol] = df
        return history_data
#    print(raw_history)
    return clean_data(raw_history, symbols)

def get_df(symbol):
    return historical_fetch([symbol])[symbol]

#fetch live prices

def live_fetch(symbols, api_key, api_secret):
    prices = {}
    async def on_bar(bar):
        prices[bar.symbol] = bar.close
    try:
        stream = StockDataStream(api_key, api_secret)
        stream.subscribe_bars(on_bar, symbols)  # Subscribe to all symbols at once
        stream.run()
        return prices
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {}

#Functions exported: live_fetch, historical_fetch
#Variables exported: NONE