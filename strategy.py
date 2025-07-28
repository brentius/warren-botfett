import pandas as pd
import numpy as np
from ta.volatility import BollingerBands
from ta.momentum import KAMAIndicator, RSIIndicator
from ta.trend import MACD

def momentum(df):
    kama = KAMAIndicator(close = df["close"], window = 20).kama().iloc[-1]
    price = df["close"].iloc[-1]
    momentum = (price - kama) / kama

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

def rsi(df):
    rsi = RSIIndicator(df["close"]).rsi().iloc[-1]

    if rsi < 30:
        conf = min(1.0, (30 - rsi) / 20)  # max at RSI 10
        return {"action": "BUY", "confidence": conf}
    elif rsi > 70:
        conf = min(1.0, (rsi - 70) / 20)  # max at RSI 90
        return {"action": "SELL", "confidence": conf}
    else:
        conf = 1 - abs(rsi - 50) / 20
        return {"action": "HOLD", "confidence": conf}
    
def macd(df):
    macd_diff = MACD(df["close"]).macd_diff().iloc[-1]

    if macd_diff > 0:
        conf = min(1.0, macd_diff / 0.5)
        return {"action": "BUY", "confidence": conf}
    elif macd_diff < 0:
        conf = min(1.0, abs(macd_diff) / 0.5)
        return {"action": "SELL", "confidence": conf}
    else:
        return {"action": "HOLD", "confidence": 0.0}

def breakout(df):
    high = df["high"].rolling(20).max().iloc[-1]
    low = df["low"].rolling(20).min().iloc[-1]
    price = df["close"].iloc[-1]

    if price >= high:
        conf = min(1.0, (price - low) / (high - low))
        return {"action": "BUY", "confidence": conf}
    elif price <= low:
        conf = min(1.0, (high - price) / (high - low))
        return {"action": "SELL", "confidence": conf}
    else:
        return {"action": "HOLD", "confidence": 0.5}

def strategy(df):
    strategies = [momentum, mean_reversion, rsi, macd, breakout]
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
    final_conf = scores[final_action] / sum(1 for item in votes for val in item if val == final_action)
    return{
        "action": final_action,
        "confidence": round(final_conf, 2)
    }