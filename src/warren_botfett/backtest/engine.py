"""Backtest engine skeleton: replay snapshots through strategy -> risk -> simulated fills."""

from __future__ import annotations

from dataclasses import dataclass, field

from warren_botfett.core.models import Fill, OrderBook
from warren_botfett.risk.base import RiskManager
from warren_botfett.strategies.base import Strategy


@dataclass
class BacktestResult:
    fills: list[Fill] = field(default_factory=list)


class BacktestEngine:
    def __init__(self, strategy: Strategy, risk: RiskManager) -> None:
        self.strategy = strategy
        self.risk = risk

    def run(self, books: list[OrderBook]) -> BacktestResult:
        raise NotImplementedError("TODO: fill simulation + metrics")
