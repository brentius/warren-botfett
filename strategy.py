import pandas as pd
import numpy as np
import ta
import random

#PLANS: use multiple strategies, which strategy used: determine by ranking
def momentum(historical_data):
    signals = {}
    for symbol, df in historical_data.items():
        momentum = (df["close"].iloc[-1] - df["close"].iloc[-10]) / df["close"].iloc[-10]
        if momentum > 0.02:
            conf = min(1.0, momentum / 0.05)  # cap at 100% confidence
            signal = {"action": "BUY", "confidence": round(conf, 2)}
        elif momentum < -0.02:
            conf = min(1.0, abs(momentum) / 0.05)
            signal = {"action": "SELL", "confidence": round(conf, 2)}
        else:
            conf = 1 - (abs(momentum) / 0.02)
            signal = {"action": "HOLD", "confidence": round(conf, 2)}
        signals[symbol] = signal
    return signals

def mean_reversion(historical_data):
    signals = {}
    for symbol, df in historical_data.items():
        ma = df["close"].rolling(20).mean().iloc[-1]
        std = df["close"].rolling(20).std().iloc[-1]
        price = df["close"].iloc[-1]

        z = (price - ma) / std  # z-score of deviation

        if z > 1.5:
            conf = min(1.0, (z - 1.5) / 1.5)
            signal = {"action": "SELL", "confidence": round(conf, 2)}
        elif z < -1.5:
            conf = min(1.0, (-z - 1.5) / 1.5)
            signal = {"action": "BUY", "confidence": round(conf, 2)}
        else:
            conf = 1 - abs(z) / 1.5
            signal = {"action": "HOLD", "confidence": round(conf, 2)}
        signals[symbol] = signal
    return signals
