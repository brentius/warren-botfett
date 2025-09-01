import backtrader as bt
import pandas as pd
import numpy as np

class markov:
    def __init__(self, diff = 1.0, max_alloc = 0.1, top_n = 3):
        self.diff = diff
        self.max_alloc = max_alloc
        self.top_n = top_n
    
    def evaluate(self, data):
        for stock, df in data.items():
            states = []
            for i in range(1, len(df)):
                delta = df["close"].iloc[i] - df["close"].iloc[i-1]
                if delta > self.diff:
                    states.append("up")
                elif delta < -self.diff:
                    states.append("down")
                else:
                    states.append("stable")
            
            df = df.iloc[1:]

class temp:
    def __init__(self, diff=1.0, max_alloc=0.1, top_n=3, window=250, laplace=1.0, horizon=1):
        self.diff = diff
        self.max_alloc = max_alloc
        self.top_n = top_n
        self.window = window
        self.laplace = laplace
        self.horizon = horizon
        self.states = ("Up", "Stable", "Down")

    def _get_state(self, delta):
        if delta > self.diff:
            return "Up"
        elif delta < -self.diff:
            return "Down"
        return "Stable"

    def _compute_states(self, series):
        """Convert price series to state sequence."""
        deltas = series.diff()
        return deltas.apply(self._get_state).dropna()

    def _transition_matrix(self, states):
        """Build transition probability matrix with Laplace smoothing."""
        idx = list(self.states)
        counts = pd.DataFrame(self.laplace, index=idx, columns=idx)
        prev, nxt = states[:-1], states[1:]
        for a, b in zip(prev, nxt):
            counts.loc[a, b] += 1
        return counts.div(counts.sum(axis=1), axis=0)

    def _predict_probs(self, matrix, current_state, n):
        """Predict n-step ahead probabilities using matrix power."""
        if current_state not in matrix.index:
            return pd.Series([1/len(self.states)] * len(self.states), index=self.states)
        Pn = np.linalg.matrix_power(matrix.values, n)
        idx = list(matrix.index)
        vec = np.zeros(len(idx))
        vec[idx.index(current_state)] = 1
        return pd.Series(vec @ Pn, index=matrix.columns)

    def evaluate(self, price_data: dict[str, pd.Series], portfolio_value: float):
        """
        price_data: {symbol: Series of closes}
        portfolio_value: current portfolio value
        Returns: {symbol: {"signal": +1/-1/0, "size": shares, "confidence": prob}}
        """
        results = {}

        for symbol, series in price_data.items():
            if len(series) < 20:  # not enough data
                continue

            series = series.iloc[-self.window:]  # apply rolling window
            states = self._compute_states(series)
            if len(states) < 2:
                continue

            current_state = states.iloc[-1]
            matrix = self._transition_matrix(states)
            probs = self._predict_probs(matrix, current_state, self.horizon)

            up_p = probs["Up"]
            down_p = probs["Down"]

            # Decide signal and confidence
            if up_p > down_p and up_p > 0.6:
                signal = 1
                confidence = up_p
            elif down_p > up_p and down_p > 0.6:
                signal = -1
                confidence = down_p
            else:
                signal = 0
                confidence = max(up_p, down_p)

            # Position sizing: allocate max_alloc * portfolio_value per trade
            price = series.iloc[-1]
            alloc_cash = portfolio_value * self.max_alloc
            size = int(alloc_cash // price) if signal != 0 else 0

            results[symbol] = {"signal": signal, "size": size, "confidence": confidence}

        # If top_n is used, filter by confidence
        if self.top_n > 0 and len(results) > self.top_n:
            sorted_syms = sorted(results.items(), key=lambda x: x[1]["confidence"], reverse=True)
            top_syms = dict(sorted_syms[:self.top_n])
            return top_syms

        return results

class interface(bt.Strategy):
    params = (
        ("diff", 1),
        ("max_alloc", 0.1),
        ("top_n", 3),
    )

    def __init__(self):
        self.strategy = temp(
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