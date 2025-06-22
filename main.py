#main.py
#puts everything together

from data import historical_fetch
from strategy import evaluate

symbols = ["AAPL", "MSFT", "NVDA", "TSLA"]
history_data = historical_fetch(symbols, start="2025-01-01")
signals = evaluate(history_data)