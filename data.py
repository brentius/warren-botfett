#data.py
#scrape + clean price data

#imports
import pandas as pd
import yfinance
import alpaca_trade_api
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

#load api key
load_dotenv()
alpaca_api_key = os.getenv("APCA_API_KEY_ID")
alpaca_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

#REST client - connect to alpaca
from alpaca_trade_api import REST
api = REST(alpaca_api_key, alpaca_secret, base_url)

#fetch historical bars
symbols = ["AAPL", "MSFT", "NVDA", "TSLA"]
def historical_fetch(symbols, timeframe = "1Day", start = "2025-01-01"):
    history_bars = api.get_bars(
        symbols = symbols,
        timeframe = timeframe,
        start = start,
        adjustment = "raw"
    ).df
    return history_bars

def live_fetch(symbols, timeframe = "1Min", start = datetime.now(timezone.utc)):
    live_bars = api.get_bars(
        symbols = symbols,
        timeframe = timeframe,
        start = start,
        adjustment = "raw"
    ).df
    return live_bars
