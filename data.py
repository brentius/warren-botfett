from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
import backtrader as bt
import pandas as pd

def fetch_historical_data(client, symbols):
    history_data = {}
    request = StockBarsRequest(
        symbol_or_symbols = symbols,
        timeframe = TimeFrame.Day,
        start = "2020-01-01",
        adjustment = "all"
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
        history_data[symbol] = df.astype("float32")
    return history_data

def parse(df, datetime_col=None):
    df_copy = df.copy()
    if datetime_col:
        df_copy[datetime_col] = pd.to_datetime(df_copy[datetime_col])
        df_copy.set_index(datetime_col, inplace=True)
    else:
        if not pd.api.types.is_datetime64_any_dtype(df_copy.index):
            raise ValueError("oupsie wrong datetime format :3 uwu")
    df_copy.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)
    df_copy = df_copy[['Open', 'High', 'Low', 'Close', 'Volume']]
    return bt.feeds.PandasData(dataname = df_copy)

def fetch_live_data(client, symbols):
    live_prices = []
    for symbol in symbols:
        request = StockLatestQuoteRequest(symbol_or_symbols = symbol)
        latest = client.get_stock_latest_quote(request)
        quote = latest[symbol]
        live_prices.append((symbol, quote.bid_price, quote.ask_price))
    return live_prices

def save(history_data):
    for stock, df in history_data.items():
        df.to_csv(f"{stock}.csv", header = False, index = False)