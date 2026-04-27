#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet Trading Bot.

Usage examples
--------------
# Market buy
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit sell
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000

# Stop-market buy (bonus)
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 85000

# Override credentials inline (not recommended for production)
python cli.py --api-key KEY --api-secret SECRET --symbol ETHUSDT --side BUY --type MARKET --quantity 0.01
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from decimal import Decimal
from typing import Optional

from dotenv import load_dotenv

from bot.client import BinanceFuturesClient, BinanceClientError, NetworkError
from bot.logging_config import setup_logging, get_logger
from bot.orders import (
    OrderResult,
    place_market_order,
    place_limit_order,
    place_stop_market_order,
)
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)

load_dotenv()  # load .env if present


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _banner() -> None:
    print(
        "\n"
        "╔══════════════════════════════════════════════════╗\n"
        "║   Binance Futures Testnet — Trading Bot v1.0     ║\n"
        "╚══════════════════════════════════════════════════╝\n"
    )


def _print_request_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal],
    stop_price: Optional[Decimal],
) -> None:
    print("─" * 52)
    print("  ORDER REQUEST SUMMARY")
    print("─" * 52)
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price is not None:
        print(f"  Price      : {price}")
    if stop_price is not None:
        print(f"  Stop Price : {stop_price}")
    print("─" * 52)


def _print_order_result(result: OrderResult) -> None:
    if not result.success:
        print("\n  ✗ ORDER FAILED")
        print(f"  Reason: {result.error_message}\n")
        return

    print("\n  ✓ ORDER PLACED SUCCESSFULLY")
    print("─" * 52)
    print("  ORDER RESPONSE DETAILS")
    print("─" * 52)
    print(f"  Order ID        : {result.order_id}")
    print(f"  Client Order ID : {result.client_order_id}")
    print(f"  Symbol          : {result.symbol}")
    print(f"  Side            : {result.side}")
    print(f"  Type            : {result.order_type}")
    print(f"  Status          : {result.status}")
    print(f"  Orig Qty        : {result.orig_qty}")
    print(f"  Executed Qty    : {result.executed_qty}")
    if result.avg_price and result.avg_price != "0":
        print(f"  Avg Price       : {result.avg_price}")
    if result.price and result.price != "0":
        print(f"  Limit Price     : {result.price}")
    if result.time_in_force:
        print(f"  Time In Force   : {result.time_in_force}")
    print("─" * 52 + "\n")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            examples:
              # Market buy
              python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

              # Limit sell
              python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000

              # Stop-market (bonus)
              python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 85000
            """
        ),
    )

    # Credentials (fallback to env vars)
    creds = parser.add_argument_group("credentials (default: env vars API_KEY / API_SECRET)")
    creds.add_argument("--api-key", default=None, help="Binance Testnet API key")
    creds.add_argument("--api-secret", default=None, help="Binance Testnet API secret")

    # Order parameters
    order = parser.add_argument_group("order parameters")
    order.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    order.add_argument(
        "--side", required=True, choices=["BUY", "SELL"],
        help="Order side"
    )
    order.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type"
    )
    order.add_argument("--quantity", required=True, help="Order quantity")
    order.add_argument("--price", default=None, help="Limit price (required for LIMIT orders)")
    order.add_argument(
        "--stop-price", dest="stop_price", default=None,
        help="Stop price (required for STOP_MARKET orders)"
    )
    order.add_argument(
        "--tif", default="GTC",
        choices=["GTC", "IOC", "FOK"],
        help="Time-in-force for LIMIT orders (default: GTC)"
    )

    # Misc
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console log level (default: INFO)"
    )

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Setup logging early
    setup_logging(args.log_level)
    logger = get_logger("cli")

    _banner()

    # ── Resolve credentials ──────────────────────────────────────────────────
    api_key = args.api_key or os.getenv("API_KEY", "")
    api_secret = args.api_secret or os.getenv("API_SECRET", "")

    if not api_key or not api_secret:
        print(
            "ERROR: API credentials missing.\n"
            "Set API_KEY and API_SECRET environment variables, "
            "use a .env file, or pass --api-key / --api-secret.\n"
        )
        logger.error("API credentials not provided.")
        return 1

    # ── Validate inputs ──────────────────────────────────────────────────────
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValueError as exc:
        print(f"\n  ✗ VALIDATION ERROR: {exc}\n")
        logger.error("Validation error: %s", exc)
        return 1

    _print_request_summary(symbol, side, order_type, quantity, price, stop_price)

    # ── Initialise client ────────────────────────────────────────────────────
    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
    except Exception as exc:
        print(f"\n  ✗ CLIENT INIT ERROR: {exc}\n")
        logger.error("Client init error: %s", exc)
        return 1

    # ── Place order ──────────────────────────────────────────────────────────
    try:
        if order_type == "MARKET":
            result = place_market_order(client, symbol, side, quantity)

        elif order_type == "LIMIT":
            result = place_limit_order(
                client, symbol, side, quantity, price, time_in_force=args.tif
            )

        elif order_type == "STOP_MARKET":
            result = place_stop_market_order(client, symbol, side, quantity, stop_price)

        else:
            # Should never reach here due to argparse choices
            result = OrderResult.from_error(f"Unsupported order type: {order_type}")

    except BinanceClientError as exc:
        result = OrderResult.from_error(str(exc))
        logger.error("BinanceClientError: %s", exc)

    except NetworkError as exc:
        result = OrderResult.from_error(str(exc))
        logger.error("NetworkError: %s", exc)

    except Exception as exc:
        result = OrderResult.from_error(f"Unexpected error: {exc}")
        logger.error("Unexpected error: %s", exc, exc_info=True)

    _print_order_result(result)
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
