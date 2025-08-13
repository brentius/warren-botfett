import backtrader as bt
import ta
import pandas as pd

class placeholder(bt.Strategy): #SMA - just a placeholder
    params = (
        ("fast", 12),
        ("slow", 26),
        ("signal", 5),
        ("max_alloc", 0.1),
        ("top_n", 3),
    )

    def __init__(self):
        # Store MACD indicators for each data feed
        self.macds = {}
        self.signals = {}
        self.confidences = {}

        for d in self.datas:
            macd = bt.ind.MACD(
                d.close,
                period_me1=self.p.fast,
                period_me2=self.p.slow,
                period_signal=self.p.signal
            )
            self.macds[d._name] = macd
            self.signals[d._name] = bt.ind.CrossOver(macd.macd, macd.signal)

    def next(self):
        for d in self.datas:
            name = d._name
            signal = self.signals[name][0]

            #confidence
            hist = self.macds[name].macd[0] - self.macds[name].signal[0]
            conf = max(min(hist / 2, 1), 0)
            self.confidences[name] = conf

            sorted_conf = sorted(self.confidences.items(),
                             key = lambda x: x[1],
                             reverse = True)
            top_stocks = [name for name, _ in sorted_conf[:self.p.top_n]]
        
        for d in self.datas:
            name = d._name
            signal = self.signals[name][0]
            pos = self.getposition(d).size
            conf = self.confidences[name]

            size = int((self.broker.getvalue() * self.p.max_alloc) / d.close[0])

            if name in top_stocks:
                if signal > 0 and pos == 0:
                    self.buy(data=d, size = size)
                    print(f"{name}: BUY at {d.close[0]}")

                # If MACD crosses below signal → Sell
                elif signal < 0 and pos > 0:
                    self.sell(data=d, size = size)
                    print(f"{name}: SELL at {d.close[0]}")



class strategy:
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

        # Top-N selection
        top_symbols = [s for s, _ in sorted(confidences.items(), key=lambda x: x[1], reverse=True)[:self.top_n]]

        for sym in top_symbols:
            size = int((account_value * self.max_alloc) / data[sym].iloc[-1])
            results[sym]["size"] = size

        return results

class test(bt.Strategy):
    params = (("fast", 12), ("slow", 26), ("signal", 5), ("max_alloc", 0.1), ("top_n", 3),)

    def __init__(self):
        self.strategy = strategy(
            fast=self.p.fast, slow=self.p.slow, signal=self.p.signal,
            max_alloc=self.p.max_alloc, top_n=self.p.top_n
        )
        # Store historical closes for each data feed
        self.closes = {d._name: [] for d in self.datas}

    def next(self):
        # Update closes
        for d in self.datas:
            self.closes[d._name].append(d.close[0])

        # Compute signals
        signals = self.strategy.evaluate(
            {sym: pd.Series(vals) for sym, vals in self.closes.items()},
            self.broker.getvalue()
        )

        # Execute orders
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