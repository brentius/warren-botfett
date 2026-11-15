"""Interfaces for market data sources and persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from warren_botfett.core.models import Instrument, OrderBook


class DataFeed(ABC):
    """Produces order-book snapshots, live or replayed from history."""

    @abstractmethod
    def stream(self, instruments: list[Instrument]) -> AsyncIterator[OrderBook]: ...


class DataStore(ABC):
    """Persists snapshots for research and backtesting."""

    @abstractmethod
    def write(self, book: OrderBook) -> None: ...

    @abstractmethod
    def read(self, instrument: Instrument, start: datetime, end: datetime) -> list[OrderBook]: ...
