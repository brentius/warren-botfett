#broker.py
#executes trades with alpaca api

#imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
import os

#load api keys
load_dotenv()
api_key = os.getenv("APCA_API_KEY_ID")
api_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

#create client - connect to alpaca
trading_client = TradingClient(api_key, api_secret, base_url = base_url, paper = True)
account = trading_client.get_account()