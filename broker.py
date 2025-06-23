#broker.py
#executes trades with alpaca api

#imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from main import api_key, api_secret, base_url, live_data

#create client - connect to alpaca
client = TradingClient(api_key, api_secret, base_url = base_url, paper = True)

def account_info(client):
    account = client.get_account()
    return{
        "cash": float(account.cash),
        "buying_power": float(account.buying_power),
        "portfolio_value:": float(account.potfolio_value),
        "equity": float(account.equity)
    }

def open_positions(client, live_data):
    positions = client.get_call_positions()
    return{pos.symbol: float(pos.qty) for pos in positions}

def place_order(trading_client, symbol, qty, side):
    order = MarketOrderRequest(
        symbol = symbol, 
        qty = qty,
        side = OrderSide.BUY if side == "BUY" else OrderSide.SELL,
        time_in_force = TimeInForce.GTC
    )
    client.submit_order(order)

def execute(client, ranked_signals):
    account_info = account_info(client)
    open_positions = open_positions(client)

    cash = account_info["cash"]

    for signal in ranked_signals:
        symbol = signal["symbol"]
        confidence = signal["confidence"]
        position_size = signal.get("position_size", 0.1) #default 10% per trade

        if symbol in open_positions: #skip if already holding stock
            continue

        allocation = cash * position_size
        price = live_data

        qty = int(allocation // price)
        if qty > 0:
            place_order(client, symbol, qty, "BUY")