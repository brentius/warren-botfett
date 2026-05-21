# does data cleaning + scraping off Alpaca API
import os
from datetime import datetime

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame


def get_client():

    api_key = os.environ.get("ALPACA_API_KEY", "data-api-key")
    secret_key = os.environ.get("ALPACA_SECRET_KEY", "secret-key")
    return StockHistoricalDataClient(api_key, secret_key)


def fetch_ohlcv(
    symbols: list[str],
    start: datetime,
    end: datetime | None = None,
    timeframe: TimeFrame = TimeFrame.Day,
    client: StockHistoricalDataClient | None = None,
):
    
    client = client or get_client()

    request = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=timeframe,
        start=start,
        end=end,
    )
    bars = client.get_stock_bars(request)

    # bars.df is a MultiIndex (symbol, timestamp) DataFrame.
    df = bars.df
    result: dict[str, pd.DataFrame] = {}
    if df.empty:
        return result

    for symbol in df.index.get_level_values("symbol").unique():
        symbol_df = df.xs(symbol, level="symbol").copy()
        result[symbol] = clean(symbol_df)

    return result


def clean(df: pd.DataFrame):
    core = [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]

    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    df = df.dropna(how="all")
    df = df.dropna(subset=core)

    price_cols = [c for c in ("open", "high", "low", "close") if c in df.columns]
    if price_cols:
        df = df[(df[price_cols] > 0).all(axis=1)]
    if "volume" in df.columns:
        df = df[df["volume"] >= 0]

    return df
