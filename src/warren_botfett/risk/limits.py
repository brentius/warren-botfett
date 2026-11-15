"""Simple hard-limit risk manager driven by the `risk:` config block."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from warren_botfett.core.models import Order, OrderType, Position, Signal
from warren_botfett.risk.base import RiskManager


class LimitsRiskManager(RiskManager):
    def __init__(self, config: dict[str, Any]) -> None:
        self.max_position_usd = Decimal(str(config.get("max_position_usd", 100)))
        self.max_total_exposure_usd = Decimal(str(config.get("max_total_exposure_usd", 500)))

    def evaluate(self, signal: Signal, positions: list[Position]) -> Order | None:
        if signal.limit_price is None:
            return None
        notional = signal.size * signal.limit_price
        exposure = sum((abs(p.size) * p.avg_price for p in positions), Decimal(0))
        if notional > self.max_position_usd:
            return None
        if exposure + notional > self.max_total_exposure_usd:
            return None
        return Order(
            instrument=signal.instrument,
            side=signal.side,
            size=signal.size,
            type=OrderType.LIMIT,
            price=signal.limit_price,
        )
