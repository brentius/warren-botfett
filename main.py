from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from dotenv import load_dotenv
import os
from data import fetch_historical_data, fetch_live_data
from strategy import evaluate
from rank import rank_buy, rank_sell
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
print(signals)

ranked_buy = rank_buy(signals, top_n = 3, conf_threshold = 0.5)
ranked_sell = rank_sell(signals, top_n = 3, conf_threshold = 0.5)
print(ranked_buy, ranked_sell)

extracted_buy = [(t[0], t[1]['action'], t[1]['confidence']) for t in ranked_buy]
extracted_sell = [(t[0], t[1]['action'], t[1]['confidence']) for t in ranked_sell]
print(extracted_buy, extracted_sell)

qty = 0

for item in extracted_buy:
    place_order(tradeclient, symbol = item[0], qty = qty, order_side = item[2])