import pandas as pd
import backtrader as bt

def test(model, weights, data):
    probs = model.predict_proba(data)
    last = probs[-1]

    position = sum(weights[i] * last[i] for i in range(len(last)))
    return position