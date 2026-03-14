#!/usr/bin/env python3
"""
cli.py — Command-line interface for the Binance Futures Testnet trading bot.

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 95000
  python cli.py --symbol ETHUSDT --side BUY --type STOP_LIMIT --quantity 0.1 --price 2400 --stop-price 2380
"""

import argparse
import json
import os
import sys

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logger
from bot.orders import place_market_order, place_limit_order, place_stop_limit_order
from bot.validators import (
    validate_symbol, validate_side, validate_order_type,
    validate_quantity, validate_price, validate_stop_price,
    ValidationError,
)

logger = setup_logger("cli")

# ── Credentials ────────────────────────────────────────────────────────────────
# Set these as environment variables or pass via --api-key / --api-secret flags.
DEFAULT_API_KEY = os.environ.get("BINANCE_TESTNET_API_KEY", "")
DEFAULT_API_SECRET = os.environ.get("BINANCE_TESTNET_API_SECRET", "")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Credentials
    creds = parser.add_argument_group("credentials (or set env vars)")
    creds.add_argument("--api-key", default=DEFAULT_API_KEY, help="Binance Testnet API key")
    creds.add_argument("--api-secret", default=DEFAULT_API_SECRET, help="Binance Testnet API secret")

    # Order parameters
    order = parser.add_argument_group("order parameters")
    order.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    order.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side")
    order.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT"],
        help="Order type",
    )
    order.add_argument("--quantity", required=True, help="Order quantity")
    order.add_argument("--price", default=None, help="Limit price (required for LIMIT and STOP_LIMIT)")
    order.add_argument("--stop-price", default=None, help="Stop trigger price (required for STOP_LIMIT)")
    order.add_argument(
        "--time-in-force", default="GTC",
        choices=["GTC", "IOC", "FOK"],
        help="Time-in-force for LIMIT orders (default: GTC)",
    )

    return parser


def print_summary(order_type: str, symbol: str, side: str, quantity: float,
                  price=None, stop_price=None):
    print("\n" + "═" * 50)
    print("  ORDER REQUEST SUMMARY")
    print("═" * 50)
    print(f"  Symbol    : {symbol}")
    print(f"  Side      : {side}")
    print(f"  Type      : {order_type}")
    print(f"  Quantity  : {quantity}")
    if price:
        print(f"  Price     : {price}")
    if stop_price:
        print(f"  Stop Price: {stop_price}")
    print("═" * 50 + "\n")


def print_result(result: dict):
    print("✅  ORDER PLACED SUCCESSFULLY")
    print("─" * 50)
    for key, val in result.items():
        if val is not None and val != "":
            print(f"  {key:<15}: {val}")
    print("─" * 50 + "\n")


def main():
    parser = build_parser()
    args = parser.parse_args()

    # ── Validate credentials ───────────────────────────────────────────────────
    if not args.api_key or not args.api_secret:
        parser.error(
            "API credentials required. Set BINANCE_TESTNET_API_KEY / BINANCE_TESTNET_API_SECRET "
            "environment variables, or pass --api-key and --api-secret."
        )

    # ── Validate inputs ────────────────────────────────────────────────────────
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)

        price = None
        stop_price = None

        if order_type in ("LIMIT", "STOP_LIMIT"):
            if not args.price:
                parser.error(f"--price is required for {order_type} orders.")
            price = validate_price(args.price)

        if order_type == "STOP_LIMIT":
            if not args.stop_price:
                parser.error("--stop-price is required for STOP_LIMIT orders.")
            stop_price = validate_stop_price(args.stop_price)

    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n❌  Validation error: {exc}\n", file=sys.stderr)
        sys.exit(1)

    # ── Print request summary ──────────────────────────────────────────────────
    print_summary(order_type, symbol, side, quantity, price, stop_price)
    logger.info(
        "Order request | type=%s symbol=%s side=%s qty=%s price=%s stopPrice=%s",
        order_type, symbol, side, quantity, price, stop_price,
    )

    # ── Place order ────────────────────────────────────────────────────────────
    client = BinanceClient(api_key=args.api_key, api_secret=args.api_secret)

    try:
        if order_type == "MARKET":
            result = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            result = place_limit_order(client, symbol, side, quantity, price, args.time_in_force)
        else:  # STOP_LIMIT
            result = place_stop_limit_order(
                client, symbol, side, quantity, price, stop_price, args.time_in_force
            )
    except BinanceAPIError as exc:
        logger.error("API error placing order: %s", exc)
        print(f"\n❌  API Error [{exc.code}]: {exc.message}\n", file=sys.stderr)
        sys.exit(1)
    except ConnectionError as exc:
        logger.error("Network error: %s", exc)
        print(f"\n❌  Network Error: {exc}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n❌  Unexpected error: {exc}\n", file=sys.stderr)
        sys.exit(1)

    print_result(result)


if __name__ == "__main__":
    main()
