# Backtesting framework built on the `backtesting` library.
# Each symbol is simulated independently (one Backtest per symbol).
import pandas as pd
from backtesting import Backtest, Strategy


_RENAME = {"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Reshape `data.fetch_ohlcv` output (lowercase cols) into what backtesting.py expects."""
    out = df.rename(columns=_RENAME)
    keep = [c for c in ("Open", "High", "Low", "Close", "Volume") if c in out.columns]
    return out[keep].copy()


class MomentumStrategy(Strategy):
    """Long-only momentum: buy on positive N-day return above a confidence floor; close on negative."""

    lookback = 20
    threshold = 0.5

    def init(self) -> None:
        pass

    def next(self) -> None:
        close = self.data.Close
        if len(close) <= self.lookback:
            return
        latest = float(close[-1])
        past = float(close[-1 - self.lookback])
        if past == 0:
            return
        ret = (latest - past) / past
        confidence = min(abs(ret) / 0.10, 1.0)
        if confidence < self.threshold:
            return
        if ret > 0 and not self.position:
            self.buy()
        elif ret < 0 and self.position:
            self.position.close()


def run_symbol(
    df: pd.DataFrame,
    strategy_cls: type[Strategy] = MomentumStrategy,
    *,
    cash: float = 100_000.0,
    commission: float = 0.0,
) -> tuple[Backtest, pd.Series]:
    bt = Backtest(_prepare(df), strategy_cls, cash=cash, commission=commission, finalize_trades=True)
    return bt, bt.run()


def run_many(
    bars: dict[str, pd.DataFrame],
    strategy_cls: type[Strategy] = MomentumStrategy,
    *,
    cash: float = 100_000.0,
    commission: float = 0.0,
) -> dict[str, pd.Series]:
    results: dict[str, pd.Series] = {}
    for symbol, df in bars.items():
        if df.empty:
            continue
        _, stats = run_symbol(df, strategy_cls, cash=cash, commission=commission)
        results[symbol] = stats
    return results
