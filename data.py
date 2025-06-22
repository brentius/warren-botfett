#data.py
#scrape + clean price data

#imports
import pandas as pd
import yfinance
import alpaca_trade_api
from dotenv import load_dotenv
import os

#load api key
load_dotenv()
alpaca_api_key = os.getenv("APCA_API_KEY_ID")
alpaca_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

#REST client - connect to alpaca
from alpaca_trade_api import REST
api = REST(alpaca_api_key, alpaca_secret, base_url)

#fetch historical bars + clean
symbols = ["AAPL", "MSFT", "NVDA", "TSLA"]
def historical_fetch(symbols, timeframe = "1Day", start = "2025-01-01"):
    raw_history = api.get_bars(symbols, timeframe, start = start, adjustment = "raw").df
    def clean_data(raw_history, symbols):
        history_data = {}
        for symbol in symbols:
            df = raw_history.loc[symbol].copy()
            df.index = pd.datetime(df.index)
            df.index = df.index.tz_convert("America/New York")
            df.sort_index(inplace = True)
            df.columns = [col.lower() for col in df.columns]
            df.dropna(inplace = True)
            history_data[symbol] = df
    return clean_data(raw_history, symbols)