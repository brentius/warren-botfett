"""The contract every exchange / prediction-market adapter implements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from warren_botfett.core.models import Fill, Instrument, Order, OrderBook, Position
from warren_botfett.core.registry import Registry


class Venue(ABC):
    """Abstract trading venue (Polymarket, Kalshi, a stock broker, a paper simulator...)."""

    name: str = "base"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    # lifecycle
    async def connect(self) -> None:  # noqa: B027 - optional hook
        """Authenticate / open sessions."""

    async def close(self) -> None:  # noqa: B027 - optional hook
        """Release resources."""

    # market data
    @abstractmethod
    async def list_instruments(self, **filters: Any) -> list[Instrument]: ...

    @abstractmethod
    async def get_order_book(self, instrument: Instrument) -> OrderBook: ...

    def stream_order_books(self, instruments: list[Instrument]) -> AsyncIterator[OrderBook]:
        """Optional websocket stream. Default: not supported."""
        raise NotImplementedError(f"{self.name} does not support streaming")

    # trading
    @abstractmethod
    async def place_order(self, order: Order) -> Order: ...

    @abstractmethod
    async def cancel_order(self, order: Order) -> None: ...

    @abstractmethod
    async def get_positions(self) -> list[Position]: ...

    async def get_fills(self) -> list[Fill]:
        return []


venue_registry: Registry[Venue] = Registry("venue")
