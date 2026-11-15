# Architecture

## Design principles

1. **Venue-agnostic core.** Strategies, risk, and portfolio code only touch `core.models` types. Adapters translate venue-native objects at the boundary.
2. **Signals, not orders.** Strategies express intent. The `RiskManager` decides whether and how much to trade.
3. **Same code for backtest, paper, and live.** Only the `Venue` and `DataFeed` implementations change.
4. **Plugins by registry.** Venues and strategies register by name so config can select them. Third-party packages can register their own.

## Adding a venue

```python
from warren_botfett.venues.base import Venue, venue_registry

@venue_registry.register("myexchange")
class MyExchange(Venue):
    async def list_instruments(self, **filters): ...
    async def get_order_book(self, instrument): ...
    async def place_order(self, order): ...
    async def cancel_order(self, order): ...
    async def get_positions(self): ...
```

## Adding a strategy

```python
from warren_botfett.strategies.base import Strategy, strategy_registry

@strategy_registry.register("my_strategy")
class MyStrategy(Strategy):
    def on_book(self, book):
        return []  # list[Signal]
```

## Prediction-market notes

- Binary outcome prices live in [0, 1] and are read as implied probabilities.
- Polymarket: each market has YES and NO outcome tokens (`clobTokenIds`). We model each token as one `Instrument`.
- Fees, tick sizes, and minimum order sizes differ by venue. Keep them in `Instrument.metadata`.
