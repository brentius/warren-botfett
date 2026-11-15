"""Polymarket venue adapter.

- Market discovery: Gamma API  (https://gamma-api.polymarket.com)
- Order books & trading: CLOB API (https://clob.polymarket.com) via `py-clob-client`

Read-only market data works today; trading methods are stubbed until auth is wired up.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

import httpx

from warren_botfett.core.models import (
    Instrument,
    InstrumentKind,
    Order,
    OrderBook,
    OrderBookLevel,
    Position,
)
from warren_botfett.venues.base import Venue, venue_registry

GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"


@venue_registry.register("polymarket")
class PolymarketVenue(Venue):
    name = "polymarket"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._http = httpx.AsyncClient(timeout=10)
        self._clob_url = self.config.get("host", CLOB_URL)

    async def close(self) -> None:
        await self._http.aclose()

    async def list_instruments(self, **filters: Any) -> list[Instrument]:
        params = {"active": "true", "closed": "false", "limit": filters.get("limit", 50)}
        resp = await self._http.get(f"{GAMMA_URL}/markets", params=params)
        resp.raise_for_status()
        instruments: list[Instrument] = []
        for m in resp.json():
            # Gamma returns these fields as JSON-encoded strings
            token_ids = json.loads(m.get("clobTokenIds") or "[]")
            outcomes = json.loads(m.get("outcomes") or "[]")
            for token_id, outcome in zip(token_ids, outcomes, strict=False):
                instruments.append(
                    Instrument(
                        venue=self.name,
                        symbol=token_id,
                        kind=InstrumentKind.BINARY_OUTCOME,
                        description=f"{m.get('question', '')} [{outcome}]",
                        metadata={"market_id": m.get("id"), "outcome": outcome},
                    )
                )
        return instruments

    async def get_order_book(self, instrument: Instrument) -> OrderBook:
        resp = await self._http.get(
            f"{self._clob_url}/book", params={"token_id": instrument.symbol}
        )
        resp.raise_for_status()
        data = resp.json()

        def levels(raw: list[dict[str, str]], descending: bool) -> list[OrderBookLevel]:
            lv = [OrderBookLevel(price=Decimal(x["price"]), size=Decimal(x["size"])) for x in raw]
            return sorted(lv, key=lambda x: x.price, reverse=descending)

        return OrderBook(
            instrument=instrument,
            bids=levels(data.get("bids", []), descending=True),
            asks=levels(data.get("asks", []), descending=False),
        )

    async def place_order(self, order: Order) -> Order:
        raise NotImplementedError("Polymarket trading not wired up yet (needs py-clob-client auth)")

    async def cancel_order(self, order: Order) -> None:
        raise NotImplementedError

    async def get_positions(self) -> list[Position]:
        raise NotImplementedError
