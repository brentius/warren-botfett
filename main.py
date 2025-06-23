#main.py
#puts everything together

from data import historical_fetch, live_fetch
from strategy import evaluate
from ranking import rank
from broker import execute, client
from dotenv import load_dotenv
import os

#load api keys
load_dotenv()
api_key = os.getenv("APCA_API_KEY_ID")
api_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

#define symbols, fetch + clean historical data
symbols = ["AAPL", "MSFT", "NVDA", "TSLA"]
history_data = historical_fetch(symbols, start="2025-01-01")
live_data = live_fetch(symbols)

#evaluate signals based on strategy - BUY / HOLD / SELL
signals = evaluate(history_data)
ranked_signals = rank(signals)

#execute
execute(client, ranked_signals)