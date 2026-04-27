"""
Order placement logic.

Each function builds the correct parameter set for a given order type,
delegates to BinanceFuturesClient.new_order(), and returns a structured
OrderResult dataclass for easy consumption by the CLI layer.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional

from bot.client import BinanceFuturesClient
from bot.logging_config import get_logger

logger = get_logger("orders")


@dataclass
class OrderResult:
    """Parsed, display-ready summary of a Binance order response."""

    success: bool
    order_id: Optional[int] = None
    client_order_id: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    order_type: Optional[str] = None
    status: Optional[str] = None
    orig_qty: Optional[str] = None
    executed_qty: Optional[str] = None
    avg_price: Optional[str] = None
    price: Optional[str] = None
    time_in_force: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "OrderResult":
        return cls(
            success=True,
            order_id=response.get("orderId"),
            client_order_id=response.get("clientOrderId"),
            symbol=response.get("symbol"),
            side=response.get("side"),
            order_type=response.get("type"),
            status=response.get("status"),
            orig_qty=response.get("origQty"),
            executed_qty=response.get("executedQty"),
            avg_price=response.get("avgPrice"),
            price=response.get("price"),
            time_in_force=response.get("timeInForce"),
            raw=response,
        )

    @classmethod
    def from_error(cls, message: str) -> "OrderResult":
        return cls(success=False, error_message=message)


# ---------------------------------------------------------------------------
# Public order functions
# ---------------------------------------------------------------------------

def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
) -> OrderResult:
    """Place a MARKET order."""
    params = dict(
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=str(quantity),
    )
    logger.info(
        "Placing MARKET order | symbol=%s side=%s qty=%s",
        symbol, side, quantity,
    )
    response = client.new_order(**params)
    result = OrderResult.from_response(response)
    logger.info(
        "MARKET order placed | orderId=%s status=%s executedQty=%s avgPrice=%s",
        result.order_id, result.status, result.executed_qty, result.avg_price,
    )
    return result


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
    time_in_force: str = "GTC",
) -> OrderResult:
    """Place a LIMIT order (default GTC)."""
    params = dict(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=str(quantity),
        price=str(price),
        timeInForce=time_in_force,
    )
    logger.info(
        "Placing LIMIT order | symbol=%s side=%s qty=%s price=%s tif=%s",
        symbol, side, quantity, price, time_in_force,
    )
    response = client.new_order(**params)
    result = OrderResult.from_response(response)
    logger.info(
        "LIMIT order placed | orderId=%s status=%s price=%s qty=%s",
        result.order_id, result.status, result.price, result.orig_qty,
    )
    return result


def place_stop_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    stop_price: Decimal,
) -> OrderResult:
    """Place a STOP_MARKET order (bonus order type)."""
    params = dict(
        symbol=symbol,
        side=side,
        type="STOP_MARKET",
        quantity=str(quantity),
        stopPrice=str(stop_price),
    )
    logger.info(
        "Placing STOP_MARKET order | symbol=%s side=%s qty=%s stopPrice=%s",
        symbol, side, quantity, stop_price,
    )
    response = client.new_order(**params)
    result = OrderResult.from_response(response)
    logger.info(
        "STOP_MARKET order placed | orderId=%s status=%s stopPrice=%s qty=%s",
        result.order_id, result.status, stop_price, result.orig_qty,
    )
    return result
