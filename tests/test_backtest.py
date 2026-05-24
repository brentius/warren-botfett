import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest import HMMRegimeStrategy, MomentumStrategy, run_symbol  # noqa: E402


def _make_bars(prices: list[float], start: str = "2024-01-01") -> pd.DataFrame:
    ts = pd.date_range(start=start, periods=len(prices), freq="D")
    df = pd.DataFrame(
        {
            "open": prices,
            "high": prices,
            "low": prices,
            "close": prices,
            "volume": [1_000_000] * len(prices),
        },
        index=ts,
    )
    df.index.name = "timestamp"
    return df


def test_rising_series_makes_money():
    prices = [100.0 + i for i in range(60)]
    MomentumStrategy.lookback = 20
    MomentumStrategy.threshold = 0.1
    _, stats = run_symbol(_make_bars(prices), MomentumStrategy, cash=10_000.0)
    assert stats["Return [%]"] > 0


def test_flat_series_no_trades():
    prices = [100.0] * 60
    MomentumStrategy.lookback = 20
    MomentumStrategy.threshold = 0.1
    _, stats = run_symbol(_make_bars(prices), MomentumStrategy, cash=10_000.0)
    assert stats["# Trades"] == 0
    assert stats["Return [%]"] == 0


def test_hmm_strategy_trades_on_rising_series():
    prices = [100.0 + i for i in range(120)]
    _, stats = run_symbol(_make_bars(prices), HMMRegimeStrategy, cash=10_000.0)
    assert stats["# Trades"] > 0


def test_determinism():
    prices = [100.0 + (i % 7) * 0.5 + i * 0.1 for i in range(80)]
    MomentumStrategy.lookback = 20
    MomentumStrategy.threshold = 0.5
    _, s1 = run_symbol(_make_bars(prices), MomentumStrategy, cash=10_000.0)
    _, s2 = run_symbol(_make_bars(prices), MomentumStrategy, cash=10_000.0)
    assert s1["Return [%]"] == s2["Return [%]"]
    assert s1["# Trades"] == s2["# Trades"]
    assert s1["Equity Final [$]"] == s2["Equity Final [$]"]
