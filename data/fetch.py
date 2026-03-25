'''
inputs: alpaca api, websocket feed, stocks.yaml symbols, .env
outputs: raw ohlcv, tick stream, order book snapshots
'''
import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv
from alpaca.data.live import StockDataStream
from alpaca.data.historical import StockHistoricalDataClient

#config
load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")