from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from datetime import datetime
import pandas as pd

def fetch_historical_data(client, symbols):
    history_data = {}
    request = StockBarsRequest(
        symbol_or_symbols = symbols,
        timeframe = TimeFrame.Day,
        start = "2025-01-01"
    )
    raw_historical_data = client.get_stock_bars(request).df

    for symbol in symbols:
        if symbol not in raw_historical_data.index.levels[0]:
            continue
        df = raw_historical_data.loc[symbol].copy()
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace = True)
        df.columns = [col.strip().lower() for col in df.columns]
        df.dropna(subset = ['close'], inplace=True)
        history_data[symbol] = df
    return history_data

def fetch_live_data(client, symbols):
    live_prices = []
    for symbol in symbols:
        request = StockLatestQuoteRequest(symbol_or_symbols = symbol)
        latest = client.get_stock_latest_quote(request)
        quote = latest[symbol]
        live_prices.append((symbol, quote.bid_price, quote.ask_price))
    return live_prices