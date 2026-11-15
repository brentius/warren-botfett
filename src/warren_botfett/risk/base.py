from __future__ import annotations

from abc import ABC, abstractmethod

from warren_botfett.core.models import Order, Position, Signal


class RiskManager(ABC):
    """Gatekeeper between strategies and execution."""

    @abstractmethod
    def evaluate(self, signal: Signal, positions: list[Position]) -> Order | None:
        """Return a sized Order, or None to reject the signal."""
