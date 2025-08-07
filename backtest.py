import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def run_backtest(evaluate, historical_data, capital, lookback = 20):
    portfolio = {}
    portfolio_history = {}
    trades = []
    dates = historical_data[next(iter(historical_data))].index

    for idx in range(lookback - 1, len(dates)):
        current_date = dates[idx]
        daily_data = {
            stock: df.loc[:current_date]
            for stock, df in historical_data.items()
            if current_date in df.index
        }

        if len(daily_data) < len(historical_data):
                day_value = sum(
                    info["quantity"] * historical_data[stock].loc[current_date]["close"]
                    for stock, info in portfolio.items()
                    if current_date in historical_data[stock].index
                )
                portfolio_history[current_date] = day_value + capital
                continue
        extracted = evaluate(daily_data)
        for stock, action, confidence in extracted:
            price = historical_data[stock].loc[current_date]["close"]
            alloc = capital * 0.1 * confidence
            quantity = 1
            if action == "BUY":
                portfolio[stock] = {
                    "buy_price": price,
                    "quantity": quantity
                }

                trades.append({
                    "stock": stock,
                    "action": action,
                    "price": price,
                    "quantity": quantity
                })
                capital -= price * quantity

            elif action == "SELL" and stock in portfolio:
                buy_price = portfolio[stock]["buy_price"]
                quantity = portfolio[stock]["quantity"]
                trades.append({
                    "stock": stock,
                    "action": action,
                    "price": price,
                    "quantity": info["quantity"],
                    "profit": (price - buy_price) * quantity
                })
                capital += price * info["quantity"]
                del portfolio[stock]

        day_value = 0
        for stock, info in portfolio.items():
            if current_date in historical_data[stock].index:
                price = historical_data[stock].loc[current_date]["close"]
                holding_value = info["quantity"] * price
                day_value += holding_value
            portfolio_history[current_date] = day_value + capital

    portfolio_history_df = pd.Series(portfolio_history).to_frame(name = "total_value")
    for stock, info in portfolio.items():
        final_price = historical_data[stock].iloc[-1]["close"]
        quantity = portfolio[stock]["quantity"]
        trades.append({
            "stock": stock,
            "action": "SELL",
            "price": final_price,
            "quantity": info["quantity"],
            "profit": (final_price - info["buy_price"]) * info["quantity"]
        })
        capital += price * info["quantity"]

    def compute_metrics(portfolio_df, trades):
            values = portfolio_df["total_value"]
            values = values[values > 0]
            returns = values.pct_change().dropna()

            cumulative_return = (values.iloc[-1] / values.iloc[0]) - 1

            if returns.std() == 0:
                sharpe_ratio = float("nan")
            else:
                sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)

            roll_max = values.cummax()
            drawdown = values / roll_max - 1
            max_drawdown = drawdown.min()

            realized_trades = realized_trades = [t for t in trades if t.get("action") == "SELL"]
            if realized_trades:
                wins = sum(1 for t in realized_trades if t["profit"] > 0)
                win_rate = wins / len(realized_trades)
            else:
                win_rate = float("nan")

            print(trades)
            print(f"Final Portfolio Value: ${values.iloc[-1]:.2f}")
            print(f"Final capital: ${capital}")
            print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
            print(f"Cumulative Return: {cumulative_return:.2%}")
            print(f"Max Drawdown: {max_drawdown:.2%}")
            print(f"Win Rate: {win_rate:.2%} ({wins} / {len(realized_trades)} trades)")

            return {
                "final_value": values.iloc[-1],
                "sharpe_ratio": sharpe_ratio,
                "cumulative_return": cumulative_return,
                "max_drawdown": max_drawdown,
                "win_rate": win_rate,
            }
    
    compute_metrics(portfolio_history_df, trades)

    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_history_df.index, portfolio_history_df["total_value"], label="Portfolio Value", linewidth=2)
    plt.title("Backtest Portfolio Performance (Daily Bars)")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()