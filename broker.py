from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

def place_order(client, symbol, qty, order_side):
    order = MarketOrderRequest(
        symbol = symbol,
        qty = qty,
        side = OrderSide.BUY if order_side == "BUY" else OrderSide.SELL,
        time_in_force = TimeInForce.GTC
        )
    client.submit_order(order)