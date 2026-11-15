"""Strategy contract: consume market data, emit Signals. Strategies never place orders."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from warren_botfett.core.models import Fill, OrderBook, Signal
from warren_botfett.core.registry import Registry


class Strategy(ABC):
    name: str = "base"

    def __init__(self, params: dict[str, Any] | None = None) -> None:
        self.params = params or {}

    @abstractmethod
    def on_book(self, book: OrderBook) -> list[Signal]:
        """React to a new order-book snapshot."""

    def on_fill(self, fill: Fill) -> None:  # noqa: B027 - optional hook
        """React to one of our orders filling."""


strategy_registry: Registry[Strategy] = Registry("strategy")
