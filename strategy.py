import backtrader as bt

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