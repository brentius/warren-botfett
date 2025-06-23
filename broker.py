#broker.py
#executes trades with alpaca api

#imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from main import api_key, api_secret, base_url

#create client - connect to alpaca
trading_client = TradingClient(api_key, api_secret, base_url = base_url, paper = True)
account = trading_client.get_account()