#main.py
#puts everything together

from data import historical_fetch, live_fetch, get_df
from strategy import evaluate
from ranking import rank
from broker import execute, account_info, open_positions, close, client
from risk import calculate_position_size, is_allowed, check_exposure, stop_loss

#define symbols, fetch + clean historical data
symbols = ["AAPL", "MSFT", "NVDA", "TSLA"]
final_trades = []
top_n = 3
min_confidence = 0.8
risk_perc = 0.05

cash = account_info["cash"]
entry_price = open_positions["entry_price"]
positions = open_positions(client)
equity = account_info["equity"]

history_data = historical_fetch(symbols, start="2025-01-01")
live_price = live_fetch(symbols)

#evaluate signals based on strategy - BUY / HOLD / SELL
signals = evaluate(history_data)
ranked_signals = rank(signals, top_n, min_confidence)

for symbol, pos in positions.items():
    if stop_loss(pos["entry_price"], live_price[symbol]):
        close(client, symbol)

for signal in ranked_signals:
    signal = ranked_signals["symbol"]
    if not check_exposure(symbol, positions, equity, max_total_allocation = 0.7):
        continue
    if is_allowed(symbol, positions):
        size = calculate_position_size(equity, live_price["symbol"], positions)
        if size > 0:
            signal["position_size"] = size
            final_trades.append(signal)

#execute
execute(client, ranked_signals, live_price)