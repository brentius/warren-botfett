import pandas as pd
import numpy as np
from ta.volatility import BollingerBands
from ta.momentum import KAMAIndicator

def momentum(df):
    momentum = KAMAIndicator(close = df["close"], window = 20)

    if momentum > 0.02:
        conf = min(1.0, momentum / 0.05)  # cap at 100% confidence
        return{"action": "BUY", "confidence": conf}
    elif momentum < -0.02:
        conf = min(1.0, abs(momentum) / 0.05)
        return{"action": "SELL", "confidence": conf}
    else:
        conf = 1 - (abs(momentum) / 0.02)
        return{"action": "HOLD", "confidence": conf}

def mean_reversion(df):
    bb = BollingerBands(close = df["close"], window = 20, window_dev = 2)
    lower = bb.bollinger_lband()
    upper = bb.bollinger_hband()
    mid = bb.bollinger_mavg()
    price = df["close"].iloc[-1]

    if price < lower.iloc[-1]:
        distance = (mid.iloc[-1] - price) / mid.iloc[-1]
        return {"action": "BUY", "confidence": min(distance * 10, 1.0)}
    elif price > upper.iloc[-1]:
        distance = (price - mid.iloc[-1]) / mid.iloc[-1]
        return {"action": "SELL", "confidence": min(distance * 10, 1.0)}
    else:
        return {"action": "HOLD", "confidence": 1 - abs(price - mid.iloc[-1]) / mid.iloc[-1]}

def evaluate(df):
    strategies = [momentum, mean_reversion]
    scores = {
        "BUY": 0.0,
        "HOLD": 0.0,
        "SELL": 0.0
    }
    votes = []
    for strategy in strategies:
        result = strategy(df)
        action = result["action"]
        confidence = result["confidence"]
        scores[action] += confidence
        votes.append((strategy.__name__, action, confidence))
    final_action = max(scores, key = scores.get)
    final_conf = scores[final_action] / len(strategies)
    return{
        "action": final_action,
        "confidence": round(final_conf, 2)
    }