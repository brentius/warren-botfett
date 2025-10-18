import pandas as pd
import backtrader as bt
import numpy as np
from hmmlearn import hmm

def HiddenMarkov(df):
    data = df["close"].to_numpy()

    scores = list()
    models = list()
    for n_components in range(1, 5):
        for idx in range(10):
            model = hmm.GaussianHMM(n_components=n_components, random_state=idx, n_iter=10)
            model.fit(data[:, None])
            models.append(model)
            scores.append(model.score(data[:, None]))
            print(f"Converged: {model.monitor_.converged}, Score: {scores[-1]}")

    model = models[np.argmax(scores)]
    print(f"Best score: {max(scores)} and {model.n_components} components")
    states = model.predict(data[:, None])
    return model, states, data

class placeholder(bt.Strategy):
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