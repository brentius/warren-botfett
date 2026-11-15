from __future__ import annotations

import logging

from warren_botfett.core.models import Order
from warren_botfett.venues.base import Venue

log = logging.getLogger(__name__)


class ExecutionEngine:
    def __init__(self, venues: dict[str, Venue]) -> None:
        self.venues = venues

    async def submit(self, order: Order) -> Order:
        venue = self.venues[order.instrument.venue]
        log.info("submitting %s %s @ %s on %s", order.side, order.size, order.price, venue.name)
        return await venue.place_order(order)
