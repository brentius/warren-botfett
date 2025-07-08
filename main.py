#main.py
#puts everything together

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from data import historical_fetch, live_fetch, get_df, api_key, api_secret
from strategy import evaluate
from ranking import rank
from broker import execute, account_info, open_positions, close, client
from risk import calculate_position_size, is_allowed, check_exposure, stop_loss
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("APCA_API_KEY_ID")
api_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

client = TradingClient(api_key, api_secret, paper = True)
dataclient = StockHistoricalDataClient(api_key, api_secret)

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

live_prices = live_fetch(symbols, api_key, api_secret)
print(live_prices)

for symbol, pos in positions.items():
    if stop_loss(pos["entry_price"], live_prices[symbol]):
        close(client, symbol)

for i in range(0, len(ranked_signals)):
    symbol, signal = ranked_signals[i]
    print(symbol) 
    if not check_exposure(symbol, positions, equity, max_total_allocation = 0.7):
        continue
    if is_allowed(symbol, positions):
        size = calculate_position_size(equity, live_prices[symbol], positions)
        if size > 0:
            signal["position_size"] = size
            final_trades.append(signal)

#execute
execute(client, ranked_signals, live_prices)