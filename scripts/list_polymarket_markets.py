"""Smoke test: list a few live Polymarket markets and print their top of book."""

import asyncio

from warren_botfett.venues.polymarket import PolymarketVenue


async def main() -> None:
    venue = PolymarketVenue()
    try:
        instruments = await venue.list_instruments(limit=5)
        for inst in instruments[:6]:
            book = await venue.get_order_book(inst)
            print(f"{book.best_bid!s:>6} / {book.best_ask!s:<6}  {inst.description}")
    finally:
        await venue.close()


if __name__ == "__main__":
    asyncio.run(main())
