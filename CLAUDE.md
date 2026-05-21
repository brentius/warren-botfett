# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project: Warren Botfett

A Python trading bot that scrapes/cleans stock market data via the Alpaca API and executes trades.

> **Current state:** the repo is early scaffolding. Only `main.py` (watchlist: `AAPL`, `MSFT`, `NVDA`) and `data.py` (an Alpaca `StockHistoricalDataClient`) exist; `.env` and `README.md` are empty. The Commands / Architecture / Conventions below describe the intended target structure (`src/strategies/`, `src/execution/`, `src/models/`, etc.) — most of those paths do not exist yet, so create them as the project grows rather than assuming they're present.

## Commands
Always use `uv` to manage the environment and run code — never bare `python`/`pip`.

Work inside a virtual environment. `uv` creates/uses a project-local `.venv` automatically:
```
uv venv                          # Create the .venv (once)
# activate it: PowerShell -> .venv\Scripts\Activate.ps1 ; bash -> source .venv/bin/activate
```
`uv run ...` and `uv sync` use this `.venv` automatically, so explicit activation is only needed for an interactive shell. Keep `.venv/` out of version control (gitignore it).
```
uv sync                          # Install deps from requirements.txt into the venv
uv pip install -r requirements.txt   # (equivalent explicit install)
uv add <package>                 # Add a dependency
uv run main.py                   # Start the bot (live trading)
uv run main.py --paper           # Start with paper trading account
uv run pytest                    # Run tests
uv run ruff check .              # Lint
uv run ruff format .             # Format
```
Dependencies are pinned in `requirements.txt` (the Alpaca SDK is `alpaca-py`, imported as `alpaca`).

## Architecture
- Python 3.12, async via asyncio
- Alpaca Trade API (alpaca-py) for orders, market data, and account info
- All strategies live in src/strategies/
- Order execution logic in src/execution/
- Shared types/models in src/models/ (Pydantic)

## Conventions
- Use Pydantic models for all data validation (API responses, config, signals)
- Return shape is always { data, error } — use the Result type in src/models/result.py
- Never log API keys or account IDs, even at DEBUG level
- Use the logger module (src/utils/logger.py), not print()
- All monetary values are Decimal, never float
- Load Alpaca credentials from `.env`, never hardcode them. `data.py` currently has placeholder strings (`"data-api-key"`, `"secret-key"`) inline — replace these with env-loaded values.

## Watch out for
- Tests run against Alpaca's paper trading sandbox — set ALPACA_PAPER=true in .env.test
- Run scripts/reset_test_state.py before the test suite to cancel open orders and flatten positions
- Alpaca's market data WebSocket will silently drop if you exceed the subscription limit — check ALPACA_DATA_FEED in config
- Strict type checking via mypy: no unused imports, ever
