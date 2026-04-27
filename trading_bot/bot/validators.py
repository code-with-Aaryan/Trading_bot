"""
Input validation helpers for the trading bot CLI.
All functions raise ValueError with clear messages on invalid input.
"""

from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    """Return uppercased symbol or raise ValueError."""
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValueError(
            f"Symbol '{symbol}' contains invalid characters. "
            "Use alphanumeric only, e.g. BTCUSDT."
        )
    if len(symbol) < 3 or len(symbol) > 20:
        raise ValueError(
            f"Symbol '{symbol}' length {len(symbol)} is out of range (3-20)."
        )
    return symbol


def validate_side(side: str) -> str:
    """Return uppercased side or raise ValueError."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Side '{side}' is invalid. Choose from: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Return uppercased order type or raise ValueError."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Order type '{order_type}' is invalid. "
            f"Choose from: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str) -> Decimal:
    """Parse and validate order quantity."""
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than zero, got {qty}.")
    return qty


def validate_price(price: Optional[str], order_type: str) -> Optional[Decimal]:
    """
    Parse and validate price.

    - LIMIT orders:       price is required and must be > 0.
    - STOP_MARKET orders: price is the stop price, required.
    - MARKET orders:      price must be None / not supplied.
    """
    order_type = order_type.upper()

    if order_type == "MARKET":
        if price is not None:
            raise ValueError("Price must not be specified for MARKET orders.")
        return None

    # LIMIT or STOP_MARKET
    if price is None:
        raise ValueError(f"Price is required for {order_type} orders.")
    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Price '{price}' is not a valid number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than zero, got {p}.")
    return p


def validate_stop_price(stop_price: Optional[str], order_type: str) -> Optional[Decimal]:
    """Parse stop price for STOP_MARKET orders."""
    if order_type.upper() != "STOP_MARKET":
        return None
    if stop_price is None:
        raise ValueError("--stop-price is required for STOP_MARKET orders.")
    try:
        sp = Decimal(str(stop_price))
    except InvalidOperation:
        raise ValueError(f"Stop price '{stop_price}' is not a valid number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be greater than zero, got {sp}.")
    return sp
