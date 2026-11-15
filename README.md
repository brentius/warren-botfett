# warren-botfett

A modular, open-source quantitative trading framework for **prediction markets** (Polymarket, Kalshi) and **equities**.

> ⚠️ Early development. Not financial advice. Trading involves real risk of loss. Check the laws that apply where you live before trading on any venue.

## Architecture

```
            ┌──────────────┐
 Venue  ──▶ │  Data feed   │ ──OrderBook──▶ Strategy ──Signal──▶ Risk ──Order──▶ Execution ──▶ Venue
 (market    └──────────────┘                   ▲                                    │
  data)                                         └────────────── Fill ◀──────────────┘
                                                              Portfolio
```

Every component is an interface you can swap out:

| Layer | Interface | Location |
|---|---|---|
| Domain models | `Instrument`, `OrderBook`, `Signal`, `Order`, `Fill`, `Position` | `core/models.py` |
| Venues | `Venue` | `venues/base.py` |
| Data | `DataFeed`, `DataStore` | `data/base.py` |
| Strategies | `Strategy` | `strategies/base.py` |
| Risk | `RiskManager` | `risk/base.py` |
| Execution | `ExecutionEngine` | `execution/engine.py` |
| Portfolio | `PortfolioTracker` | `portfolio/tracker.py` |
| Backtesting | `BacktestEngine` | `backtest/engine.py` |

Strategies **never** place orders directly. They emit `Signal`s; the risk layer turns them into `Order`s or rejects them.

## Layout

```
src/warren_botfett/
  core/          venue-agnostic models, plugin registry, event bus
  venues/        exchange adapters (polymarket/, kalshi/, equities/, paper.py)
  data/          live + historical feeds, storage
  strategies/    strategy base class + examples/
  risk/          pre-trade checks and sizing
  execution/     order routing
  portfolio/     positions and PnL
  backtest/      historical replay
  config.py      YAML + .env config loading
  cli.py         `botfett` command
config/          default.yaml (copy to local.yaml to override)
tests/           unit/ and integration/
notebooks/       research
scripts/         one-off utilities
docs/            design notes
```

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,polymarket]"
cp .env.example .env
botfett config
pytest
```

## Roadmap

- [x] Project scaffold and core interfaces
- [ ] Polymarket: read-only market data (Gamma + CLOB) ← in progress
- [ ] Polymarket: authenticated trading
- [ ] Data recorder + backtester
- [ ] Paper trading with simulated fills
- [ ] Kalshi adapter
- [ ] Equities adapter (Alpaca)

## Contributing

To add a venue, subclass `Venue` and decorate it with `@venue_registry.register("name")`. To add a strategy, subclass `Strategy` and use `@strategy_registry.register("name")`. See `docs/architecture.md`.

## License

MIT
