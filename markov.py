# Hidden Markov Model regime classifier: bull / bear / neutral.
from dataclasses import dataclass

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

REGIMES = ("bear", "neutral", "bull")


@dataclass
class RegimeResult:
    states: pd.Series           # per-bar regime label ("bull"/"bear"/"neutral")
    latest: str                 # most recent regime
    means: dict[str, float]     # mean log-return per regime
    model: GaussianHMM


def _log_returns(df: pd.DataFrame) -> pd.Series:
    close = df["close"].astype(float)
    return np.log(close / close.shift(1)).dropna()


def fit(df: pd.DataFrame, n_iter: int = 200, seed: int = 42) -> RegimeResult:
    if "close" not in df.columns or len(df) < 30:
        raise ValueError("need a 'close' column and at least 30 rows to fit HMM")

    returns = _log_returns(df)
    X = returns.to_numpy().reshape(-1, 1)

    model = GaussianHMM(
        n_components=3,
        covariance_type="full",
        n_iter=n_iter,
        random_state=seed,
    )
    model.fit(X)

    hidden = model.predict(X)
    # Sort hidden state indices by mean return so 0=bear, 1=neutral, 2=bull.
    order = np.argsort(model.means_.flatten())
    state_to_label = {int(order[i]): REGIMES[i] for i in range(3)}

    labels = pd.Series(
        [state_to_label[int(s)] for s in hidden],
        index=returns.index,
        name="regime",
    )
    means = {state_to_label[int(i)]: float(model.means_[i, 0]) for i in range(3)}

    return RegimeResult(
        states=labels,
        latest=str(labels.iloc[-1]),
        means=means,
        model=model,
    )


def classify(data: dict[str, pd.DataFrame]) -> dict[str, RegimeResult]:
    out: dict[str, RegimeResult] = {}
    for symbol, df in data.items():
        try:
            out[symbol] = fit(df)
        except (ValueError, RuntimeError):
            continue
    return out
