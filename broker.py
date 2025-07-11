from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

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

def place_order(client, symbol, qty, order_side):
    order = MarketOrderRequest(
        symbol = symbol,
        qty = qty,
        side = OrderSide.BUY if order_side == "BUY" else OrderSide.SELL,
        time_in_force = TimeInForce.GTC
    )
    client.submit_order(order)