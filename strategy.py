import pandas as pd
import numpy as np
import ta
import random

#PLANS: use multiple strategies, which strategy used: determine by ranking
def momentum(df):
    momentum = (df["close"].iloc[-1] - df["close"].iloc[-10]) / df["close"].iloc[-10]
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
    ma = df["close"].rolling(20).mean().iloc[-1]
    std = df["close"].rolling(20).std().iloc[-1]
    price = df["close"].iloc[-1]
    z = (price - ma) / std  # z-score of deviation
    if z > 1.5:
        conf = min(1.0, (z - 1.5) / 1.5)
        return {"action": "SELL", "confidence": conf}
    elif z < -1.5:
        conf = min(1.0, (-z - 1.5) / 1.5)
        return {"action": "BUY", "confidence": conf}
    else:
        conf = 1 - abs(z) / 1.5
        return {"action": "HOLD", "confidence": conf}

def evaluate(df):
    strategies = [mean_reversion, momentum]
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