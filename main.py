from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from dotenv import load_dotenv
import os
import asyncio
from data import fetch_historical_data, fetch_live_data
from strategy import evaluate
from rank import rank
from broker import execute

load_dotenv()
api_key = os.getenv("APCA_API_KEY_ID")
api_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

tradeclient = TradingClient(api_key, api_secret, paper = True)
dataclient = StockHistoricalDataClient(api_key, api_secret)
liveclient = StockDataStream(api_key, api_secret)

symbols = ["AAPL", "MSFT", "TSLA", "GOOG", "RKLB", "NVDA", "VKTX", "ORCL", "TGT"] #symbols - trades these stocks

historical_data = fetch_historical_data(dataclient, symbols)

#for symbol in symbols:
#    liveclient.subscribe_quotes(websocket_live, symbol)
#    data = liveclient.run()
#    live_prices.update({symbol:data})
#print(live_prices)

live_prices = fetch_live_data(dataclient, symbols)
print(live_prices)

signals = {}
for symbol, df in historical_data.items():
    result = evaluate(df)
    signals[symbol] = result
print(signals)
ranked_signals = rank(signals, top_n = 3, conf_threshold = 0.5)
print(ranked_signals)
extracted_signals = [(t[0], t[1]['action'], t[1]['confidence']) for t in ranked_signals]
print(extracted_signals)

for item in extracted_signals:
    if item[1] == "BUY":
        stockprice = live_prices[1]
    else:
        stockprice == live_prices[2]
    execute(tradeclient, stockprice, item[0], item[1], item[2])