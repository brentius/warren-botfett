import backtrader as bt
import ta
import pandas as pd

class strategy: #PLACEHOLDER
    def __init__(self, fast = 12, slow = 26, signal = 5, max_alloc = 0.1, top_n = 3):
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.max_alloc = max_alloc
        self.top_n = top_n

    def evaluate(self, data, account_value):
        results = {}
        confidences = {}
        for sym, closes in data.items():
            closes = pd.Series(closes)

            macd_ind = ta.trend.MACD(
                closes,
                window_slow = self.slow,
                window_fast = self.fast,
                window_sign = self.signal
            )
            macd_line = macd_ind.macd()
            signal_line = macd_ind.macd_signal()

            cross = macd_line.iloc[-1] - signal_line.iloc[-1]
            signal_val = 1 if cross > 0 else -1 if cross<0 else 0
            conf = max(min(cross / 2, 1), 0)

            results[sym] = {"signal": signal_val, "confidence": conf}
            confidences[sym] = conf

        top_symbols = [s for s, _ in sorted(confidences.items(), key=lambda x: x[1], reverse=True)[:self.top_n]]

        for sym in top_symbols:
            size = int((account_value * self.max_alloc) / data[sym].iloc[-1])
            results[sym]["size"] = size

        return results

class test(bt.Strategy):
    params = (
        ("fast", 12),
        ("slow", 26),
        ("signal", 5),
        ("max_alloc", 0.1),
        ("top_n", 3),
    )

    def __init__(self):
        self.strategy = strategy(
            fast=self.p.fast, slow=self.p.slow, signal=self.p.signal,
            max_alloc=self.p.max_alloc, top_n=self.p.top_n
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