"""Command-line entry point: `botfett <command>`."""

from __future__ import annotations

import argparse

from warren_botfett import __version__
from warren_botfett.config import load_config


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="botfett", description="warren-botfett trading bot")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("config", help="print the resolved config")
    sub.add_parser("run", help="run live/paper trading (not yet implemented)")
    sub.add_parser("backtest", help="run a backtest (not yet implemented)")
    args = parser.parse_args(argv)

    if args.command == "config":
        import pprint

        pprint.pprint(load_config())
    else:
        raise SystemExit(f"'{args.command}' is not implemented yet")


if __name__ == "__main__":
    main()
