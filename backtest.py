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
            continue
        extracted = evaluate(daily_data)
        for stock, action, confidence in extracted:
            price = historical_data[stock].loc[current_date]["close"]
            quantity = int((capital / len(extracted)) / price)

            if action == "BUY" and stock not in portfolio:
                portfolio[stock] = {
                    "buy_price": price,
                    "quantity": quantity
                }
                
                trades.append({
                    "stock": stock,
                    "entry_date": current_date,
                    "buy_price": price,
                    "quantity": quantity
                })

        day_value = 0
        for stock, info in portfolio.items():
            if current_date in historical_data[stock].index:
                price = historical_data[stock].loc[current_date]["close"]
                holding_value = info["quantity"] * price
                day_value += holding_value
        portfolio_history[current_date] = day_value

    portfolio_history_df = pd.Series(portfolio_history).to_frame(name="total_value")

    for stock, info in portfolio.items():
        final_price = historical_data[stock].iloc[-1]["close"]
        trades.append({
            "stock": stock,
            "exit_date": historical_data[stock].index[-1],
            "sell_price": final_price,
            "entry_date": info.get("entry_date", "N/A"),
            "buy_price": info["buy_price"],
            "quantity": info["quantity"],
            "profit": (final_price - info["buy_price"]) * info["quantity"]
        })

    def compute_backtest_metrics(portfolio_df, trades):
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

        realized_trades = [t for t in trades if "profit" in t]
        if realized_trades:
            wins = sum(1 for t in realized_trades if t["profit"] > 0)
            win_rate = wins / len(realized_trades)
        else:
            win_rate = float("nan")

        print(f"Final Portfolio Value: ${values.iloc[-1]:.2f}")
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
    
    compute_backtest_metrics(portfolio_history_df, trades)

    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_history_df.index, portfolio_history_df["total_value"], label="Portfolio Value", linewidth=2)
    plt.title("Backtest Portfolio Performance (Daily Bars)")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()