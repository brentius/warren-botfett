#broker.py
#executes trades with alpaca api

#imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from data import api_key, api_secret, base_url

#create client - connect to alpaca
client = TradingClient(api_key, api_secret, paper = True)

def account_info(client):
    account = client.get_account()
    return{
        "cash": float(account.cash),
        "buying_power": float(account.buying_power),
        "portfolio_value:": float(account.portfolio_value),
        "equity": float(account.equity)
    }

def open_positions(client):
    positions = client.get_all_positions()
    return {
        pos.symbol: {
            "qty": float(pos.qty),
            "entry_price": float(pos.avg_entry_price),
            "market_value": float(pos.market_value),
            "unrealized_pl": float(pos.unrealized_pl)
        }
        for pos in positions
    }

def place_order(client, symbol, qty, side):
    order = MarketOrderRequest(
        symbol = symbol,
        qty = qty,
        side = OrderSide.BUY if side == "BUY" else OrderSide.SELL,
        time_in_force = TimeInForce.GTC
    )
    client.submit_order(order)

def execute(client, ranked_signals, live_price):
    account_info = account_info(client)
    positions = open_positions(client)

    cash = account_info["cash"]

    for signal in ranked_signals:
        symbol = signal["symbol"]
        confidence = signal["confidence"]
        position_size = signal.get("position_size", 0.1) #default 10% per trade

        if symbol in positions: #skip if already holding stock
            continue

        allocation = cash * position_size
        price = live_price

        qty = int(allocation // price)
        if qty > 0:
            place_order(client, symbol, qty, "BUY")

def close(client, symbol):
    positions = client.get_all_positions()
    symbols = [p.symbol for p in positions]
    if symbol in symbols:
        client.close_position(symbol)