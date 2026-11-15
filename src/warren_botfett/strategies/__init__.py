"""Trading strategies. Subclass `Strategy` and register with `strategy_registry`."""

from warren_botfett.strategies.base import Strategy, strategy_registry

__all__ = ["Strategy", "strategy_registry"]
