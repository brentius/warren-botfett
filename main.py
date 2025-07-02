#main.py
#puts everything together

from data import historical_fetch, live_fetch, get_df
from strategy import evaluate
from ranking import rank
from broker import execute, account_info, open_positions, close, client
from risk import calculate_position_size, is_allowed, check_exposure, stop_loss

#define symbols, fetch + clean historical data
symbols = ["AAPL", "MSFT", "TSLA", "GOOG", "RKLB"]
final_trades = []
top_n = 3
min_confidence = 0.2
risk_perc = 0.05

accinfo = account_info(client)
positions = open_positions(client)

cash = accinfo["cash"]
equity = accinfo["equity"]
#entry_price = positions["entry_price"]

history_data = historical_fetch(symbols, start="2025-01-01")
#print(history_data)

for symbol in symbols:
    df = get_df(symbol)

#evaluate signals based on strategy - BUY / HOLD / SELL
signals = evaluate(history_data, df)
print(signals)
ranked_signals = rank(signals, top_n, min_confidence)
print(ranked_signals)

for symbol in symbols:
    live_price = live_fetch(symbol)
    print(live_price)

for symbol, pos in positions.items():
    if stop_loss(pos["entry_price"], live_price[symbol]):
        close(client, symbol)

for i in range(0, len(ranked_signals)):
    symbol, signal = ranked_signals[i]
    print(symbol) 
    if not check_exposure(symbol, positions, equity, max_total_allocation = 0.7):
        continue
    if is_allowed(symbol, positions):
        size = calculate_position_size(equity, live_price["symbol"], positions)
        if size > 0:
            signal["position_size"] = size
            final_trades.append(signal)

#execute
execute(client, ranked_signals, live_price)