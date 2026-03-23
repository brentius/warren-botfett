"""
data/fetcher.py

Fetches historical and real-time market data from Alpaca using the
alpaca-py SDK (pip install alpaca-py).

Handles:
  - Historical bars (OHLCV) for one or many symbols
  - Latest quotes and trades
  - Real-time streaming via WebSocket
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from alpaca.data import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.data.requests import (
    StockBarsRequest,
    StockLatestQuoteRequest,
    StockLatestTradeRequest,
    StockQuotesRequest,
    StockTradesRequest,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

logger = logging.getLogger(__name__)

ET = ZoneInfo("America/New_York")


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

def _make_client() -> StockHistoricalDataClient:
    """
    Build a StockHistoricalDataClient from environment variables.
    Set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env file.
    """
    api_key = os.environ["ALPACA_API_KEY"]
    secret_key = os.environ["ALPACA_SECRET_KEY"]
    return StockHistoricalDataClient(api_key, secret_key)


# ---------------------------------------------------------------------------
# Historical bars
# ---------------------------------------------------------------------------

def fetch_bars(
    symbols: list[str],
    timeframe: TimeFrame = TimeFrame.Day,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = None,
    feed: str = "iex",          # "iex" (free) | "sip" (paid subscription)
) -> dict[str, pd.DataFrame]:
    """
    Fetch OHLCV bars for one or more symbols.

    Args:
        symbols:   List of ticker symbols, e.g. ["AAPL", "TSLA", "NVDA"]
        timeframe: Bar size — TimeFrame.Minute, TimeFrame.Hour, TimeFrame.Day, etc.
                   For custom sizes: TimeFrame(5, TimeFrameUnit.Minute)
        start:     Start datetime (timezone-aware). Defaults to 30 days ago.
        end:       End datetime (timezone-aware). Defaults to now.
        limit:     Max bars per symbol. None = fetch all (paginates automatically).
        feed:      Data feed. Free accounts use "iex"; SIP requires paid plan.

    Returns:
        Dict mapping symbol → DataFrame with columns:
            open, high, low, close, volume, trade_count, vwap
        Index is a DatetimeIndex (UTC).
    """
    if start is None:
        start = datetime.now(ET) - timedelta(days=30)
    if end is None:
        end = datetime.now(ET)

    client = _make_client()

    request = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=timeframe,
        start=start,
        end=end,
        limit=limit,
        feed=feed,
    )

    logger.info(
        "Fetching %s bars for %d symbol(s) from %s to %s",
        timeframe,
        len(symbols),
        start.date(),
        end.date(),
    )

    bars = client.get_stock_bars(request)

    # .df gives a MultiIndex DataFrame (symbol, timestamp); unstack to per-symbol
    result: dict[str, pd.DataFrame] = {}
    raw_df = bars.df  # MultiIndex: (symbol, timestamp)

    for symbol in symbols:
        try:
            df = raw_df.loc[symbol].copy()
            df.index = pd.to_datetime(df.index, utc=True)
            result[symbol] = df
        except KeyError:
            logger.warning("No bar data returned for %s", symbol)

    return result


# Convenience wrappers for common timeframes
def fetch_daily_bars(symbols: list[str], days: int = 90, **kwargs) -> dict[str, pd.DataFrame]:
    start = datetime.now(ET) - timedelta(days=days)
    return fetch_bars(symbols, TimeFrame.Day, start=start, **kwargs)


def fetch_minute_bars(symbols: list[str], days: int = 5, **kwargs) -> dict[str, pd.DataFrame]:
    start = datetime.now(ET) - timedelta(days=days)
    return fetch_bars(symbols, TimeFrame.Minute, start=start, **kwargs)


def fetch_hourly_bars(symbols: list[str], days: int = 30, **kwargs) -> dict[str, pd.DataFrame]:
    start = datetime.now(ET) - timedelta(days=days)
    return fetch_bars(symbols, TimeFrame.Hour, start=start, **kwargs)


def fetch_custom_bars(
    symbols: list[str],
    amount: int,
    unit: TimeFrameUnit,
    days: int = 30,
    **kwargs,
) -> dict[str, pd.DataFrame]:
    """E.g. fetch_custom_bars(['AAPL'], 5, TimeFrameUnit.Minute)"""
    start = datetime.now(ET) - timedelta(days=days)
    return fetch_bars(symbols, TimeFrame(amount, unit), start=start, **kwargs)


# ---------------------------------------------------------------------------
# Latest snapshots (quotes & trades)
# ---------------------------------------------------------------------------

def fetch_latest_quotes(symbols: list[str], feed: str = "iex") -> dict:
    """
    Fetch the latest NBBO quote for each symbol.

    Returns:
        Dict mapping symbol → Quote object with fields:
            .ask_price, .ask_size, .bid_price, .bid_size, .timestamp
    """
    client = _make_client()
    request = StockLatestQuoteRequest(symbol_or_symbols=symbols, feed=feed)
    quotes = client.get_stock_latest_quote(request)
    logger.info("Fetched latest quotes for: %s", symbols)
    return quotes  # keyed by symbol


def fetch_latest_trades(symbols: list[str], feed: str = "iex") -> dict:
    """
    Fetch the latest trade for each symbol.

    Returns:
        Dict mapping symbol → Trade object with fields:
            .price, .size, .timestamp, .exchange
    """
    client = _make_client()
    request = StockLatestTradeRequest(symbol_or_symbols=symbols, feed=feed)
    trades = client.get_stock_latest_trade(request)
    logger.info("Fetched latest trades for: %s", symbols)
    return trades


def fetch_latest_prices(symbols: list[str], feed: str = "iex") -> dict[str, float]:
    """
    Convenience: returns a simple {symbol: last_price} dict.
    """
    trades = fetch_latest_trades(symbols, feed=feed)
    return {symbol: trade.price for symbol, trade in trades.items()}


# ---------------------------------------------------------------------------
# Historical trades & quotes (tick data)
# ---------------------------------------------------------------------------

def fetch_trades(
    symbols: list[str],
    start: datetime,
    end: datetime,
    feed: str = "iex",
) -> dict[str, pd.DataFrame]:
    """Fetch tick-level trade data for the given window."""
    client = _make_client()
    request = StockTradesRequest(
        symbol_or_symbols=symbols,
        start=start,
        end=end,
        feed=feed,
    )
    trades = client.get_stock_trades(request)
    raw_df = trades.df

    result = {}
    for symbol in symbols:
        try:
            df = raw_df.loc[symbol].copy()
            df.index = pd.to_datetime(df.index, utc=True)
            result[symbol] = df
        except KeyError:
            logger.warning("No trade data for %s", symbol)
    return result


def fetch_quotes(
    symbols: list[str],
    start: datetime,
    end: datetime,
    feed: str = "iex",
) -> dict[str, pd.DataFrame]:
    """Fetch tick-level quote data for the given window."""
    client = _make_client()
    request = StockQuotesRequest(
        symbol_or_symbols=symbols,
        start=start,
        end=end,
        feed=feed,
    )
    quotes = client.get_stock_quotes(request)
    raw_df = quotes.df

    result = {}
    for symbol in symbols:
        try:
            df = raw_df.loc[symbol].copy()
            df.index = pd.to_datetime(df.index, utc=True)
            result[symbol] = df
        except KeyError:
            logger.warning("No quote data for %s", symbol)
    return result


# ---------------------------------------------------------------------------
# Real-time WebSocket streaming
# ---------------------------------------------------------------------------

class AlpacaStreamer:
    """
    Streams live bars, quotes, and trades via WebSocket.

    Usage:
        streamer = AlpacaStreamer(["AAPL", "TSLA"])
        streamer.on_bar = my_bar_handler
        asyncio.run(streamer.start())
    """

    def __init__(self, symbols: list[str], feed: str = "iex"):
        api_key = os.environ["ALPACA_API_KEY"]
        secret_key = os.environ["ALPACA_SECRET_KEY"]
        self.symbols = symbols
        self.stream = StockDataStream(api_key, secret_key, feed=feed)

    # Override these with your own handlers
    async def on_bar(self, bar) -> None:
        logger.info("[BAR] %s | O:%.2f H:%.2f L:%.2f C:%.2f V:%d",
                    bar.symbol, bar.open, bar.high, bar.low, bar.close, bar.volume)

    async def on_quote(self, quote) -> None:
        logger.info("[QUOTE] %s | Bid:%.2f Ask:%.2f", quote.symbol, quote.bid_price, quote.ask_price)

    async def on_trade(self, trade) -> None:
        logger.info("[TRADE] %s | Price:%.2f Size:%d", trade.symbol, trade.price, trade.size)

    def start(self) -> None:
        """Subscribe and start the event loop (blocking)."""
        self.stream.subscribe_bars(self.on_bar, *self.symbols)
        self.stream.subscribe_quotes(self.on_quote, *self.symbols)
        self.stream.subscribe_trades(self.on_trade, *self.symbols)

        logger.info("Starting live stream for: %s", self.symbols)
        self.stream.run()

    def stop(self) -> None:
        self.stream.stop()


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT"]

    # --- Historical daily bars ---
    print("\n=== Daily Bars (last 10 days) ===")
    bars = fetch_daily_bars(WATCHLIST, days=10)
    for sym, df in bars.items():
        print(f"{sym}: {len(df)} bars | last close: {df['close'].iloc[-1]:.2f}")

    # --- Latest prices ---
    print("\n=== Latest Prices ===")
    prices = fetch_latest_prices(WATCHLIST)
    for sym, price in prices.items():
        print(f"  {sym}: ${price:.2f}")

    # --- 5-min bars ---
    print("\n=== 5-Minute Bars (last 2 days) ===")
    intraday = fetch_custom_bars(WATCHLIST, 5, TimeFrameUnit.Minute, days=2)
    for sym, df in intraday.items():
        print(f"  {sym}: {len(df)} 5-min bars")