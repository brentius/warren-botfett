#Data.py
#Job: Get and clean price data

#imports
import pandas
import yfinance
import alpaca_trade_api
from dotenv import load_dotenv
import os

#load api key
load_dotenv()
alpaca_api_key = os.getenv("APCA_API_KEY_ID")
alpaca_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

#REST client
from alpaca_trade_api import REST
api = REST(alpaca_api_key, alpaca_secret, base_url)

