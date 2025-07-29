import pandas as pd
import matplotlib.pyplot as plt

def run_backtest(evaluate, historical_data, capital, lookback = 20):
    portfolio = {}
    portfolio_history = {}
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

        day_value = 0
        for stock, info in portfolio.items():
            if current_date in historical_data[stock].index:
                price = historical_data[stock].loc[current_date]["close"]
                holding_value = info["quantity"] * price
                day_value += holding_value
        portfolio_history[current_date] = day_value
    portfolio_history_df = pd.Series(portfolio_history).to_frame(name="total_value")

    final_value = portfolio_history_df["total_value"].iloc[-1]
    portfolio_history_df["returns"] = portfolio_history_df["total_value"].pct_change()
    rf = 0
    excess_returns = portfolio_history_df["returns"] - rf
    sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * (252 ** 0.5)
    monthly_returns = portfolio_history_df["total_value"].resample("M").last().pct_change() * 100  # in %
    cumulative_return = (portfolio_history_df["total_value"].iloc[-1] / portfolio_history_df["total_value"].iloc[0]) - 1
    rolling_max = portfolio_history_df["total_value"].cummax()
    drawdown = portfolio_history_df["total_value"] / rolling_max - 1
    max_drawdown = drawdown.min()

    print(f"Final Portfolio Value: ${final_value:.2f}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Cumulative Return: {cumulative_return:.2f}")
    print(f"Max Drawdown: {max_drawdown*100:.2f}%")
    print("\nMonthly ROI (%):")
    print(monthly_returns.dropna().round(2))

    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_history_df.index, portfolio_history_df["total_value"], label="Portfolio Value", linewidth=2)
    plt.title("Backtest Portfolio Performance (Daily Bars)")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()