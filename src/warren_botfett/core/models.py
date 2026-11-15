"""Venue-agnostic domain models.

Every venue adapter translates its native objects into these types, so strategies,
risk, and portfolio code never depend on a specific exchange.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(UTC)


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    LIMIT = "limit"
    MARKET = "market"


class OrderStatus(StrEnum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class InstrumentKind(StrEnum):
    BINARY_OUTCOME = "binary_outcome"  # Polymarket / Kalshi contract
    EQUITY = "equity"


class Instrument(BaseModel):
    """A tradeable thing: a prediction-market outcome token or a stock."""

    venue: str
    symbol: str  # venue-native id (e.g. Polymarket token_id, Kalshi ticker, AAPL)
    kind: InstrumentKind
    description: str = ""
    expires_at: datetime | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class OrderBookLevel(BaseModel):
    price: Decimal
    size: Decimal


class OrderBook(BaseModel):
    instrument: Instrument
    bids: list[OrderBookLevel] = Field(default_factory=list)
    asks: list[OrderBookLevel] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=_now)

    @property
    def best_bid(self) -> Decimal | None:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> Decimal | None:
        return self.asks[0].price if self.asks else None

    @property
    def mid(self) -> Decimal | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid + self.best_ask) / 2


class Signal(BaseModel):
    """A strategy's intent. Risk turns signals into orders (or rejects them)."""

    strategy: str
    instrument: Instrument
    side: Side
    size: Decimal
    limit_price: Decimal | None = None
    confidence: float = 1.0
    reason: str = ""
    timestamp: datetime = Field(default_factory=_now)


class Order(BaseModel):
    instrument: Instrument
    side: Side
    size: Decimal
    type: OrderType = OrderType.LIMIT
    price: Decimal | None = None
    client_id: str | None = None
    venue_id: str | None = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=_now)


class Fill(BaseModel):
    order_venue_id: str
    instrument: Instrument
    side: Side
    price: Decimal
    size: Decimal
    fee: Decimal = Decimal(0)
    timestamp: datetime = Field(default_factory=_now)


class Position(BaseModel):
    instrument: Instrument
    size: Decimal = Decimal(0)
    avg_price: Decimal = Decimal(0)
    realized_pnl: Decimal = Decimal(0)
