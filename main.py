#main.py
#puts everything together

from data import historical_fetch, clean_data
from strategy import evaluate

symbols = ["AAPL", "MSFT", "NVDA", "TSLA"]
raw_history = historical_fetch(symbols, start="2025-01-01")
history_data = clean_data(raw_history, symbols)
signals = evaluate(history_data)