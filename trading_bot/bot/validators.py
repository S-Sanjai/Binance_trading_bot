"""
validators.py — Input validation for CLI arguments.
"""

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


class ValidationError(Exception):
    pass


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s.isalpha() or len(s) < 5:
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected something like BTCUSDT or ETHUSDT."
        )
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}."
        )
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return t


def validate_quantity(quantity: str) -> float:
    try:
        q = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if q <= 0:
        raise ValidationError(f"Quantity must be greater than 0. Got: {q}")
    return q


def validate_price(price: str) -> float:
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Price must be greater than 0. Got: {p}")
    return p


def validate_stop_price(stop_price: str) -> float:
    try:
        p = float(stop_price)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Stop price must be greater than 0. Got: {p}")
    return p
