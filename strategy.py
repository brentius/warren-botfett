import pandas as pd
import backtrader as bt
import numpy as np
from hmmlearn import hmm

def HiddenMarkov(df):
    price = df["close"].to_numpy()
    returns = np.diff(np.log(price))
    data = returns.reshape(-1, 1)
    scores = []
    models = []

    for n_components in range(1, 5):
        for idx in range(10):
            model = hmm.GaussianHMM(n_components=n_components, random_state=idx, n_iter=40)
            model.fit(data)
            models.append(model)
            scores.append(model.score(data))
            print(f"Converged: {model.monitor_.converged}, Score: {scores[-1]}")

    model = models[np.argmax(scores)]
    print(f"Best score: {max(scores)} and {model.n_components} components")
    states = model.predict(data)

    def describe_states(model, states, returns):
        stats = []
        for s in range(model.n_components):
            idx = states == s
            r = returns[idx]
            stats.append({
                "state": s,
                "mean_ret": np.mean(r),
                "vol": np.std(r),
                "freq": np.sum(idx),
            })
        return stats
    
    stats = describe_states(model, states, returns)
    for s in stats:
        print(s)

    return model, states, data


class exampleStrategy(bt.Strategy):
    params = dict(
        pfast=10,
        pslow=30
    )

    def __init__(self):
        sma1=bt.ind.SMA(period=self.p.pfast)
        sma2=bt.ind.SMA(period=self.p.pslow)
        self.crossover=bt.ind.CrossOver(sma1, sma2)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        
        elif self.crossover < 0:
            self.close()