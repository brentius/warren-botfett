import backtrader as bt
import pandas as pd
import numpy as np

class HiddenMarkov(self, )

class interface(bt.Strategy):
    params = (
        ("diff", 1),
        ("max_alloc", 0.1),
        ("top_n", 3),
    )

    def __init__(self):
        self.strategy = HiddenMarkov(
            diff=self.p.diff,
            max_alloc=self.p.max_alloc,
            top_n=self.p.top_n
        )
        self.closes = {d._name: [] for d in self.datas}

    def next(self):
        for d in self.datas:
            self.closes[d._name].append(d.close[0])

        signals = self.strategy.evaluate(
            {sym: pd.Series(vals) for sym, vals in self.closes.items()},
            self.broker.getvalue()
        )

        for d in self.datas:
            name = d._name
            sig_info = signals.get(name)
            if not sig_info:
                continue

            signal_val = sig_info.get("signal", 0)
            size = sig_info.get("size", 0)
            pos = self.getposition(d).size

            if signal_val > 0 and pos == 0:
                self.buy(data=d, size=size)
            elif signal_val < 0 and pos > 0:
                self.sell(data=d, size=size)