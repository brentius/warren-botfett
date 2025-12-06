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
    print(f"Best: {max(scores)}, {model.n_components} components")
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
                "sharpe": np.mean(r)/np.std(r),
            })
            stats = sorted(stats, key=lambda x: x['sharpe'], reverse=True)
            probs = model.predict_proba(data.reshape(-1,1))
        return stats, probs

    stats = describe_states(model, states, returns)

    for item in stats:
        print(item)
    
    return model, states, stats