#strategy.py
#trading logic

#imports
import pandas as pd
import numpy as np
import ta
from typing import Dict, Any

#PLANS: use multiple strategies, which strategy used: determine by ranking
def momentum(df):
    momentum = df["close"].pct_change(10).iloc[-1]
    rsi = df["momentum_rsi"].iloc[-1]

    if momentum > 0.02 and rsi > 55:
        return{"action": "buy", "confidence": min(momentum / 0.05, 1.0)}
    elif momentum < -0.02 and rsi < 45:
        return{"action": "sell", "confidence": min(abs(momentum / 0.05, 1.0))}
    else:
        return{"action": "hold", "confidence": 1 - abs(momentum) / 0.02}

#evaluate strategy
def evaluate(history_data, df):
    signals = {}
    return signals