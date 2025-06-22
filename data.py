#data.py
#scrape + clean price data

#imports
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
#from alpaca.data.live import StockDataStream
#from alpaca.data.models import Trade
from dotenv import load_dotenv
import os

#load api keys
load_dotenv()
alpaca_api_key = os.getenv("APCA_API_KEY_ID")
alpaca_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

#create client - connect to alpaca
client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret)

#fetch historical bars + clean
symbols = ["AAPL", "MSFT", "NVDA", "TSLA"]

def clean_data(raw_history, symbols):
    history_data = {}
    for symbol in symbols:
        df = raw_history.loc[symbol].copy()
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize("UTC").tz_convert("America/New York")
        df.sort_index(inplace = True)
        df.columns = [col.lower() for col in df.columns]
        df.dropna(inplace = True)
        history_data[symbol] = df
    return history_data

def historical_fetch(symbols, timeframe = TimeFrame.Day, start = "2025-01-01"):
    request = StockBarsRequest(
        symbol_or_symbols = symbols,
        start = start,
        timeframe = timeframe
    )
    raw_history = client.get_stock_bars(request).df
    return clean_data(raw_history, symbols)