from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from dotenv import load_dotenv
import os
from data import fetch_historical_data, fetch_live_data
from strategy import evaluate
from rank import rank
from broker import place_order

load_dotenv()
api_key = os.getenv("APCA_API_KEY_ID")
api_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

tradeclient = TradingClient(api_key, api_secret, paper = True)
dataclient = StockHistoricalDataClient(api_key, api_secret)
liveclient = StockDataStream(api_key, api_secret)

symbols = ["AAPL", "MSFT", "TSLA", "GOOG", "RKLB"] #symbols - trades these stocks

historical_data = fetch_historical_data(dataclient, symbols)
live_data = fetch_live_data(liveclient, symbols)

signals = evaluate(historical_data) #evaluate based on signals
ranked_signals = rank(signals, top_n = 3, conf_threshold = 0.5)
extracted_signals = [(t[0], t[1]['action'], t[1]['confidence']) for t in ranked_signals]

for item in extracted_signals:
    place_order(tradeclient, symbol = item[0], qty = 0, order_side = item[2])