"""Toy strategy: buy when the ask is below a fair value by more than `edge_threshold`."""

from __future__ import annotations

from decimal import Decimal

from warren_botfett.core.models import OrderBook, Side, Signal
from warren_botfett.strategies.base import Strategy, strategy_registry


@strategy_registry.register("example_threshold")
class ThresholdStrategy(Strategy):
    name = "example_threshold"

    def fair_value(self, book: OrderBook) -> Decimal | None:
        # Placeholder model: replace with something that actually has edge.
        fv = self.params.get("fair_values", {}).get(book.instrument.symbol)
        return Decimal(str(fv)) if fv is not None else None

    def on_book(self, book: OrderBook) -> list[Signal]:
        fv = self.fair_value(book)
        ask = book.best_ask
        if fv is None or ask is None:
            return []
        edge = fv - ask
        if edge <= Decimal(str(self.params.get("edge_threshold", 0.05))):
            return []
        return [
            Signal(
                strategy=self.name,
                instrument=book.instrument,
                side=Side.BUY,
                size=Decimal(str(self.params.get("size", 10))),
                limit_price=ask,
                confidence=float(edge),
                reason=f"fv={fv} ask={ask} edge={edge}",
            )
        ]
