# WARREN BOTFETT

A systematic, event-driven algorithmic trading bot designed to run on a Raspberry Pi 5. Takes in data from the Alpaca SDK, runs it through a strategy that you bring on your own, and outputs buy/hold/sell signals. Includes layered risk management, and remote control via Discord - all within a modular architecture built for reliability over uptime-sensitive hardware.

---

## Overview

Botfett is not a latency arbitrage machine. It is a strategy driven system that generates signals from a strategy you bring yourself, passes them through a risk layer, and executes via Alpaca, with full monitoring, structured logging, and a Discord command interface for remote control.

It is designed to run headlessly on a Pi 5, survive reboots, and be observable and controllable entirely via a Discord server.

---

## Architecture

```
trading-bot/
├── config/
│   ├── settings.py          # Global settings (API keys, timeouts, env vars)
│   ├── stocks.yaml          # Watchlist, symbols, per-stock parameters
│   └── strategies.yaml      # Strategy configs (thresholds, indicators, weights)
│
├── data/
│   ├── fetcher.py           # Market data ingestion (REST + WebSocket)
│   ├── normalizer.py        # Cleaning, resampling, aligning OHLCV data
│   └── cache.py             # Redis / local caching layer
│
├── strategies/
│   ├── base.py              # Abstract Strategy class (interface contract)
│   ├── momentum.py          # Momentum / trend-following logic
│   ├── mean_reversion.py    # Mean reversion logic
│   └── ml_model.py          # ML-based signal generation (optional)
│
├── signals/
│   ├── generator.py         # Combines strategy outputs → unified signal
│   └── filters.py           # Signal filters (volatility gate, news filter, etc.)
│
├── risk/
│   ├── position_sizer.py    # Kelly, fixed-fraction, volatility-scaled sizing
│   ├── portfolio.py         # Portfolio-level exposure, correlation limits
│   └── stop_loss.py         # Trailing stops, hard stops, drawdown limits
│
├── execution/
│   ├── broker.py            # Broker API abstraction (Alpaca, IBKR, etc.)
│   ├── order_manager.py     # Order lifecycle: submit, track, cancel, fill
│   └── slippage.py          # Execution quality tracking
│
├── monitoring/
│   ├── logger.py            # Structured trade + event logging
│   ├── metrics.py           # P&L, Sharpe, drawdown, win-rate tracking
│   └── alerts.py            # Slack / email / Discord alerts on anomalies
│
├── comms/
│   ├── discord_bot.py       # Bot client, command routing, auth
│   ├── commands.py          # Command handlers (!status, !halt, !pause, etc.)
│   └── formatter.py         # Format portfolio/metric data for Discord
│
├── backtesting/
│   ├── engine.py            # Event-driven backtest runner
│   ├── simulator.py         # Order fill simulation, commission modelling
│   └── report.py            # Performance report generation
│
├── tests/
│   ├── test_strategies.py
│   ├── test_risk.py
│   └── test_execution.py
│
├── notebooks/               # Research and strategy prototyping (Jupyter)
├── main.py                  # Entry point — orchestrates the full loop
├── scheduler.py             # Cron-style job runner (market open/close hooks)
├── requirements.txt
├── .env                     # Secrets — never commit this
└── README.md
```

---

## Pipeline

Data flows in one direction through clearly separated layers. Each layer has a single responsibility and communicates via well-defined interfaces.

```
Market (REST + WebSocket)
        │
        ▼
   fetcher.py  ──►  normalizer.py  ──►  cache.py
                                            │
                        ┌───────────────────┤
                        ▼                   ▼
               momentum.py         mean_reversion.py
               ml_model.py (opt.)
                        │
                        ▼
                  generator.py  ──►  filters.py
                                          │
                                          ▼
                               position_sizer.py
                                    portfolio.py
                                    stop_loss.py
                                          │
                                          ▼
                                    broker.py
                                 order_manager.py
                                    slippage.py
                                          │
                          ┌───────────────┤
                          ▼               ▼
                     logger.py       metrics.py
                     alerts.py ──► discord_bot.py
```

---

## Discord Remote Control

The bot is controllable via a Discord bot running as a separate systemd service. All commands are restricted to a whitelist of Discord user IDs defined in `settings.py`.

| Command | Description |
|---|---|
| `!status` | Current positions, P&L, open orders, bot health |
| `!halt` | Triggers the circuit breaker — stops all activity |
| `!pause` | Stops new signals; holds existing positions |
| `!resume` | Resumes signal generation after a pause |
| `!positions` | Detailed breakdown of current holdings |
| `!metrics` | Session Sharpe, drawdown, win rate |
| `!logs [n]` | Tail the last n log lines |
| `!setparam [strategy] [key] [value]` | Adjust a strategy parameter live |

`!halt` and `!pause` route through the same circuit breaker path as `stop_loss.py` — they never bypass the risk layer.

---

## Prerequisites

- Raspberry Pi 5 (4GB RAM minimum recommended)
- Python 3.11+
- Redis (optional — falls back to in-memory cache)
- A supported broker account (Alpaca recommended for getting started)
- A Discord bot token and server

---

## Installation

```bash
# Clone the repo
git clone https://github.com/yourname/trading-bot.git
cd trading-bot

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy the example env file and fill in your secrets
cp .env.example .env
nano .env
```

---

## Configuration

All configuration lives in `config/`. You should not need to touch application code to adjust trading behaviour.

**`config/settings.py`** — broker credentials (loaded from `.env`), timeouts, log rotation policy, max position size, drawdown limit, Discord allowlist.

**`config/stocks.yaml`** — your watchlist and any per-symbol parameter overrides.

**`config/strategies.yaml`** — indicator lookback windows, signal thresholds, and strategy weights used by `generator.py`.

---

## Running

### Development (foreground)

```bash
python main.py
```

### Production (systemd — recommended for Pi)

Two services run independently: the main trading loop and the Discord bot. This ensures Discord control remains available even if the trading loop crashes.

```bash
# Copy service files
sudo cp deploy/trading-bot.service /etc/systemd/system/
sudo cp deploy/discord-bot.service /etc/systemd/system/

# Enable and start
sudo systemctl enable trading-bot discord-bot
sudo systemctl start trading-bot discord-bot

# Check status
sudo systemctl status trading-bot
sudo journalctl -u trading-bot -f
```

---

## Backtesting

The backtest engine uses the exact same strategy, signal, and risk code as the live system — no separate implementations. To run a backtest:

```bash
python -m backtesting.engine \
  --symbols AAPL MSFT \
  --start 2023-01-01 \
  --end 2024-01-01 \
  --strategy momentum
```

Output is a performance report in `reports/` containing an equity curve, drawdown chart, trade-by-trade log, and summary statistics. The metrics schema matches `monitoring/metrics.py` so you can compare backtest expectations directly against live session results.

---

## Monitoring

Logs are structured JSON written to `logs/` and rotated daily (7-day retention by default — conserve SD card space on Pi). Each log entry includes timestamp, module, event type, symbol, and a payload dict.

Key metrics tracked live by `metrics.py`:

- Session and cumulative P&L
- Sharpe ratio (rolling)
- Maximum drawdown
- Win rate and average win/loss ratio
- Order rejection rate
- Execution slippage (expected vs actual fill)

Alerts fire via Discord when any configured threshold is breached. Alert thresholds are set in `settings.py`.

---

## Raspberry Pi Notes

The Pi 5 is capable hardware for this workload, but a few things deserve attention:

**Thermal management.** Sustained CPU load during market hours will cause throttling without adequate cooling. A heatsink + fan case is strongly recommended. The bot logs Pi CPU temperature via `alerts.py` and fires an alert above the configured threshold.

**Power loss.** `order_manager.py` persists state to disk and reconciles against the broker's actual open orders on startup. A clean shutdown hook is registered in `main.py`. An uninterruptible power supply (UPS HAT) is recommended for live trading.

**Storage.** Use a quality A2-rated SD card or, preferably, boot from USB SSD. SD cards under continuous write load fail. Log rotation is aggressive by default to limit writes.

**Dependencies.** Keep the live trading path dependency-light. Do not import PyTorch or heavy ML libraries in the main loop — use ONNX Runtime for inference if `ml_model.py` is active.

---

## Safety

- **Never commit `.env`** — it is in `.gitignore` by default.
- The Discord command allowlist in `settings.py` is the only authentication layer for remote commands. Keep it to your own user ID.
- `!halt` is the emergency stop. Know the command before you go live.
- Paper trade for a meaningful period before deploying real capital. The systemd setup supports a `paper=true` flag in `.env` that routes all orders to broker paper trading endpoints.

---

## Development

```bash
# Run tests
pytest tests/

# Lint
ruff check .

# Type check
mypy .
```

New strategies must implement the interface defined in `strategies/base.py`. They receive an aligned OHLCV DataFrame and a config dict, and return a `Signal` object. They must be stateless — given the same inputs, they must always return the same output.

---

## Disclaimer

This software is for educational and research purposes. It is not financial advice. Algorithmic trading involves substantial risk of loss. You are solely responsible for any trading decisions made using this system.