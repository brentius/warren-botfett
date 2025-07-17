from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from ta.volatility import AverageTrueRange

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

def execute(tradeclient, dataclient, symbol, order_side, confidence):
    acc_info = account_info(tradeclient)
    power = acc_info["buying_power"]

    max_alloc_pct = 0.10
    alloc = power * max_alloc_pct * confidence
    price = float(dataclient.get_stock_latest_trade(symbol).price)
    quantity = int(alloc // price)

    if quantity < 1:
        print(f"[SKIP] Not enough funds to buy any shares of {symbol}")
        return None
    
    def place_order(quantity):
        order = MarketOrderRequest(
            symbol = symbol,
            qty = quantity,
            side = OrderSide.BUY if order_side == "BUY" else OrderSide.SELL,
            time_in_force = TimeInForce.GTC
        )
        tradeclient.submit_order(order)
    return place_order(quantity)