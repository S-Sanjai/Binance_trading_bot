"""
orders.py — Order placement logic for Market, Limit, and Stop-Limit orders.
Wraps BinanceClient and formats results for clean CLI output.
"""

from typing import Any, Dict, Optional

from bot.client import BinanceClient
from bot.logging_config import setup_logger

logger = setup_logger("orders")


def _format_response(resp: Dict[str, Any]) -> Dict[str, Any]:
    """Pull the most relevant fields out of the raw API response."""
    return {
        "orderId": resp.get("orderId"),
        "symbol": resp.get("symbol"),
        "side": resp.get("side"),
        "type": resp.get("type"),
        "status": resp.get("status"),
        "origQty": resp.get("origQty"),
        "executedQty": resp.get("executedQty"),
        "avgPrice": resp.get("avgPrice"),
        "price": resp.get("price"),
        "stopPrice": resp.get("stopPrice"),
        "timeInForce": resp.get("timeInForce"),
        "updateTime": resp.get("updateTime"),
    }


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
) -> Dict[str, Any]:
    """Place a MARKET order."""
    logger.info("Placing MARKET order | symbol=%s side=%s qty=%s", symbol, side, quantity)
    params = dict(symbol=symbol, side=side, type="MARKET", quantity=quantity)
    resp = client.place_order(**params)
    result = _format_response(resp)
    logger.info("MARKET order placed | orderId=%s status=%s", result["orderId"], result["status"])
    return result


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """Place a LIMIT order."""
    logger.info(
        "Placing LIMIT order | symbol=%s side=%s qty=%s price=%s tif=%s",
        symbol, side, quantity, price, time_in_force,
    )
    params = dict(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce=time_in_force,
    )
    resp = client.place_order(**params)
    result = _format_response(resp)
    logger.info("LIMIT order placed | orderId=%s status=%s", result["orderId"], result["status"])
    return result


def place_stop_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """Place a STOP_MARKET / STOP order (bonus order type)."""
    logger.info(
        "Placing STOP_LIMIT order | symbol=%s side=%s qty=%s price=%s stopPrice=%s",
        symbol, side, quantity, price, stop_price,
    )
    params = dict(
        symbol=symbol,
        side=side,
        type="STOP",
        quantity=quantity,
        price=price,
        stopPrice=stop_price,
        timeInForce=time_in_force,
    )
    resp = client.place_order(**params)
    result = _format_response(resp)
    logger.info(
        "STOP_LIMIT order placed | orderId=%s status=%s", result["orderId"], result["status"]
    )
    return result
