from decimal import Decimal

from warren_botfett.core.models import Fill, OrderBook, OrderBookLevel, Side
from warren_botfett.portfolio import PortfolioTracker
from warren_botfett.risk import LimitsRiskManager
from warren_botfett.strategies import strategy_registry
from warren_botfett.strategies.examples import ThresholdStrategy


def test_order_book_mid(yes_token):
    book = OrderBook(
        instrument=yes_token,
        bids=[OrderBookLevel(price=Decimal("0.40"), size=Decimal(100))],
        asks=[OrderBookLevel(price=Decimal("0.44"), size=Decimal(100))],
    )
    assert book.mid == Decimal("0.42")


def test_threshold_strategy_emits_signal_and_risk_sizes_it(yes_token):
    strat = ThresholdStrategy({"fair_values": {"123": 0.55}, "edge_threshold": 0.05, "size": 10})
    book = OrderBook(
        instrument=yes_token, asks=[OrderBookLevel(price=Decimal("0.44"), size=Decimal(100))]
    )
    signals = strat.on_book(book)
    assert len(signals) == 1
    order = LimitsRiskManager({"max_position_usd": 100}).evaluate(signals[0], [])
    assert order is not None and order.price == Decimal("0.44")


def test_strategy_registered():
    assert "example_threshold" in strategy_registry.names()


def test_portfolio_realized_pnl(yes_token):
    pt = PortfolioTracker()
    pt.apply_fill(Fill(order_venue_id="a", instrument=yes_token, side=Side.BUY,
                       price=Decimal("0.40"), size=Decimal(10)))
    pos = pt.apply_fill(Fill(order_venue_id="b", instrument=yes_token, side=Side.SELL,
                             price=Decimal("0.50"), size=Decimal(10)))
    assert pos.size == 0
    assert pos.realized_pnl == Decimal("1.00")
