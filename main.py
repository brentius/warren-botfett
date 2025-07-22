from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from dotenv import load_dotenv
import os
from data import fetch_historical_data, fetch_live_data
from strategy import evaluate
from rank import rank
from broker import execute, open_positions
import logging

load_dotenv()
api_key = os.getenv("APCA_API_KEY_ID")
api_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

tradeclient = TradingClient(api_key, api_secret, paper = True)
dataclient = StockHistoricalDataClient(api_key, api_secret)
liveclient = StockDataStream(api_key, api_secret)

symbols = ["AAPL", "MSFT", "TSLA", "GOOG", "NVDA", "VKTX", "ORCL", "TGT"] #symbols - trades these stocks

historical_data = fetch_historical_data(dataclient, symbols)
live_data = fetch_live_data(dataclient, symbols)
print(live_data)

signals = {}
for symbol, df in historical_data.items():
    result = evaluate(df)
    signals[symbol] = result
ranked_signals = rank(signals, top_n = 3, conf_threshold = 0.5, portfolio = open_positions(tradeclient))
print(ranked_signals)
extracted_signals = [(t[0], t[1]['action'], t[1]['confidence']) for t in ranked_signals]
print(extracted_signals)

for item in extracted_signals:
    stock, action, quantity = item
    matched = next((v for v in live_data if v[0] == stock), None)
    if not matched:
        continue
    elif action == "BUY":
        stockprice = matched[1]
    elif action == "SELL":
        stockprice = matched[2]
    else:
        continue
#    execute(tradeclient, stock, stockprice, action, quantity)
    print(f"{action} {quantity} of {stock} at {stockprice}")