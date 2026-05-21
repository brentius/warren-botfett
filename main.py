# Entry point: wires data -> strategy -> Alpaca trade execution.
import argparse
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

import data
import strategy

symbols = ["AAPL", "MSFT", "NVDA"]

CONFIDENCE_THRESHOLD = 0.5
# How far back to pull bars (must comfortably exceed the strategy lookback).
LOOKBACK_DAYS = 120


def get_trading_client(paper: bool = True) -> TradingClient:
    """Build an Alpaca trading client. paper=True -> sandbox, False -> live."""
    api_key = os.environ.get("ALPACA_API_KEY", "data-api-key")
    secret_key = os.environ.get("ALPACA_SECRET_KEY", "secret-key")
    return TradingClient(api_key, secret_key, paper=paper)


def execute(client: TradingClient, signals, qty: int = 1) -> None:
    """Submit market orders for actionable signals."""
    for sig in signals:
        if sig.action == "hold" or sig.confidence < CONFIDENCE_THRESHOLD:
            print(f"skip  {sig.stock:6} {sig.action:4} conf={sig.confidence}")
            continue

        side = OrderSide.BUY if sig.action == "buy" else OrderSide.SELL
        order = MarketOrderRequest(
            symbol=sig.stock,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY,
        )
        submitted = client.submit_order(order)
        print(
            f"order {sig.stock:6} {sig.action:4} conf={sig.confidence} "
            f"id={submitted.id}"
        )


def main(paper: bool = True) -> None:
    load_dotenv()

    mode = "PAPER" if paper else "LIVE"
    print(f"Running Warren Botfett in {mode} mode on {symbols}")

    start = datetime.now() - timedelta(days=LOOKBACK_DAYS)
    bars = data.fetch_ohlcv(symbols, start=start)

    signals = strategy.run(bars)

    client = get_trading_client(paper=paper)
    execute(client, signals)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Warren Botfett trading bot")
    # Default to paper; pass --live to trade with real money.
    parser.add_argument(
        "--live",
        action="store_true",
        help="Trade against the live account (default is paper).",
    )
    args = parser.parse_args()

    main(paper=not args.live)
