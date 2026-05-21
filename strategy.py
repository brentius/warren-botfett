# placeholder momentum strategy
from dataclasses import dataclass
import pandas as pd

@dataclass
class Signal:
    stock: str #e.g. AAPL
    action: str #buy/hold/sell
    confidence: float #[0,1]


def momentum_signal(df: pd.DataFrame, lookback: int = 20):
    if df is None or "close" not in df.columns or len(df) <= lookback:
        return None

    close = df["close"]
    latest = float(close.iloc[-1])
    past = float(close.iloc[-1 - lookback])
    if past == 0:
        return None

    ret = (latest - past) / past
    confidence = min(abs(ret) / 0.10, 1.0)

    if ret > 0:
        action = "buy"
    elif ret < 0:
        action = "sell"
    else:
        action = "hold"
        confidence = 0.0

    return Signal(stock="", action=action, confidence=round(confidence, 4))


def run(data: dict[str, pd.DataFrame], lookback = 20):
    signals: list[Signal] = []
    for symbol, df in data.items():
        sig = momentum_signal(df, lookback=lookback)
        if sig is None:
            continue
        sig.stock = symbol
        signals.append(sig)
    return signals
