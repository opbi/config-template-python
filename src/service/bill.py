from src.lib.order import total
from src.types import Order


def get_bill(order: Order) -> float:
    """Check the order and sum the bill."""
    return round(total(order), 1)
