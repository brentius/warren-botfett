import pandas as pd
import numpy as np
import ta
import random

#PLANS: use multiple strategies, which strategy used: determine by ranking
def evaluate(historical_data):
    signals = {}
    for symbol, df in historical_data.items():
        #placeholder strategy
        signal = {
            "action": "BUY" if df["close"].iloc[-1] > df["close"].mean() else "SELL",
            "confidence": round(random.random(), 2) #placeholder confidence
        }
        signals[symbol] = signal
    return signals