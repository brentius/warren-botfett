"""Paper-trading wrapper: real market data from an underlying venue, simulated fills."""

from __future__ import annotations

import uuid
from typing import Any

from warren_botfett.core.models import Instrument, Order, OrderBook, OrderStatus, Position
from warren_botfett.venues.base import Venue


class PaperVenue(Venue):
    name = "paper"

    def __init__(self, data_venue: Venue, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self.data_venue = data_venue
        self.orders: dict[str, Order] = {}

    async def list_instruments(self, **filters: Any) -> list[Instrument]:
        return await self.data_venue.list_instruments(**filters)

    async def get_order_book(self, instrument: Instrument) -> OrderBook:
        return await self.data_venue.get_order_book(instrument)

    async def place_order(self, order: Order) -> Order:
        order.venue_id = str(uuid.uuid4())
        order.status = OrderStatus.OPEN  # TODO: simulate fills against the live book
        self.orders[order.venue_id] = order
        return order

    async def cancel_order(self, order: Order) -> None:
        if order.venue_id in self.orders:
            self.orders[order.venue_id].status = OrderStatus.CANCELLED

    async def get_positions(self) -> list[Position]:
        return []
