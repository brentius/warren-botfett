#data.py
#JOB: fetch and clean stock data (turn into dataframes)

import pandas as pd
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest

def fetch_historical_data(dataclient, symbols):
    request = StockBarsRequest(
        symbol_or_symbols = symbols,
        timeframe = TimeFrame.Day,
        start = "2025-01-01"
    )
    raw_historical_data = dataclient.get_stock_bars(request).df
    def clean_data(raw_historical_data, symbols):
        history_data = {}
        for symbol in symbols:
            df = raw_historical_data.loc[symbol].copy()
            df.index = pd.to_datetime(df.index)
#           df.index = df.index.tz_localize("UTC").tz_convert("America/New_York")
            df.sort_index(inplace = True)
            df.columns = [col.lower() for col in df.columns]
            df.dropna(subset=['close'], inplace=True)
            history_data[symbol] = df
        return history_data
    return clean_data(raw_historical_data, symbols)

def fetch_live_data(liveclient, symbols):
    async def quote_handler(data):
        print(data)
    live_data = {}
    for symbol in symbols:
        data = liveclient.subscribe_quotes(quote_handler, symbol)
        live_data.update({symbol: data})
    return live_data