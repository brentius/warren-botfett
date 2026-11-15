from __future__ import annotations

from decimal import Decimal

from warren_botfett.core.models import Fill, Position, Side


class PortfolioTracker:
    def __init__(self) -> None:
        self.positions: dict[tuple[str, str], Position] = {}

    def apply_fill(self, fill: Fill) -> Position:
        key = (fill.instrument.venue, fill.instrument.symbol)
        pos = self.positions.setdefault(key, Position(instrument=fill.instrument))
        signed = fill.size if fill.side == Side.BUY else -fill.size
        new_size = pos.size + signed

        if pos.size == 0 or (pos.size > 0) == (signed > 0):
            # opening or adding to a position
            total_cost = pos.avg_price * abs(pos.size) + fill.price * fill.size
            pos.avg_price = total_cost / abs(new_size)
        else:
            # reducing, closing, or flipping
            closed = min(abs(signed), abs(pos.size))
            direction = 1 if pos.size > 0 else -1
            pos.realized_pnl += (fill.price - pos.avg_price) * closed * direction
            if new_size == 0:
                pos.avg_price = Decimal(0)
            elif (new_size > 0) != (pos.size > 0):
                pos.avg_price = fill.price

        pos.realized_pnl -= fill.fee
        pos.size = new_size
        return pos

    def all(self) -> list[Position]:
        return list(self.positions.values())
