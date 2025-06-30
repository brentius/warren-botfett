#strategy.py
#trading logic

#imports
import pandas as pd
import numpy as np
import ta
from typing import Dict, Any

#PLANS: use multiple strategies, which strategy used: determine by ranking
def evaluate(history_data, df):
    signals = {}
    for symbol, df in history_data.items():
        #placeholder strategy
        signal = {
            "action": "BUY" if df["close"].iloc[-1] > df["close"].mean() else "HOLD",
            "confidence": 0.85 #placeholder confidence
        }
        signals[symbol] = signal
    return signals