#main.py
#puts everything together

from data import historical_fetch
from strategy import evaluate

#define symbols, fetch + clean historical data
symbols = ["AAPL", "MSFT", "NVDA", "TSLA"]
history_data = historical_fetch(symbols, start="2025-01-01")

#evaluate signals based on strategy - BUY / HOLD / SELL
signals = evaluate(history_data)