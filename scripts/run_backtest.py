# CLI: pull historical bars and run the backtesting.py-based simulator per symbol.
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import data  # noqa: E402
from backtest import HMMRegimeStrategy, MomentumStrategy, run_many  # noqa: E402

_STRATEGIES = {"momentum": MomentumStrategy, "hmm": HMMRegimeStrategy}


_METRIC_KEYS = (
    "Return [%]",
    "Buy & Hold Return [%]",
    "Sharpe Ratio",
    "Max. Drawdown [%]",
    "# Trades",
    "Win Rate [%]",
    "Equity Final [$]",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest a strategy over historical bars.")
    parser.add_argument("--strategy", choices=sorted(_STRATEGIES), default="momentum")
    parser.add_argument("--symbols", default="AAPL,MSFT,NVDA")
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--cash", type=float, default=100_000.0)
    parser.add_argument("--commission", type=float, default=0.0)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--lookback", type=int, default=20)
    args = parser.parse_args()

    load_dotenv()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    start = datetime.now() - timedelta(days=args.days)

    print(f"Fetching {symbols} over last {args.days} days...")
    bars = data.fetch_ohlcv(symbols, start=start)
    if not bars:
        print("No bars returned from Alpaca.")
        return

    strategy_cls = _STRATEGIES[args.strategy]
    if strategy_cls is MomentumStrategy:
        MomentumStrategy.lookback = args.lookback
        MomentumStrategy.threshold = args.threshold

    results = run_many(bars, strategy_cls, cash=args.cash, commission=args.commission)

    for symbol, stats in results.items():
        print(f"\n=== {symbol} ===")
        for key in _METRIC_KEYS:
            if key in stats.index:
                val = stats[key]
                print(f"  {key:<22} {val}")


if __name__ == "__main__":
    main()
