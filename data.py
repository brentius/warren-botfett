import pandas as pd
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest
from alpaca.data.requests import StockLatestQuoteRequest

def fetch_historical_data(client, symbols):
    history_data = {}
    request = StockBarsRequest(
        symbol_or_symbols = symbols,
        timeframe = TimeFrame.Day,
        start = "2025-01-01"
    )
    raw_historical_data = client.get_stock_bars(request).df
    for symbol in symbols:
        df = raw_historical_data.loc[symbol].copy()
        df.index = pd.to_datetime(df.index)
#       df.index = df.index.tz_localize("UTC").tz_convert("America/New_York")
        df.sort_index(inplace = True)
        df.columns = [col.lower() for col in df.columns]
        df.dropna(subset=['close'], inplace=True)
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