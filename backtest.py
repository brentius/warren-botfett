import pandas as pd
import matplotlib.pyplot as plt

def run_backtest(extracted, df, data, capital):
    portfolio = {}
    portfolio_history = pd.DataFrame(index = data[next(iter(data))].index)
    for stock, action in extracted:
        price = data[stock].iloc[-1]["close"]
        quantity = int((capital/len(extracted))/price)

        if action == "BUY":
            portfolio[stock] = {
                "buy_price": price,
                "quantity": quantity,
                "history": df["close"] * quantity
            }
        
    for stock, data in portfolio.items():
        portfolio_history[stock] = data["history"]

    portfolio_history["total_value"] = portfolio_history.sum(axis = 1)
    final_value = portfolio_history["total_value"].iloc[-1]

    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_history.index, portfolio_history["total_value"], label="Portfolio Value", linewidth=2)
    for stock in portfolio:
        plt.plot(portfolio_history.index, portfolio_history[stock], linestyle="--", alpha=0.7, label=stock)
    plt.title("Backtest Portfolio Performance")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()