from src.data import MENU
from src.types import Number, Order


def total(order: Order) -> Number:
    """Sum the price of all items on the order."""
    return sum([MENU[k] * v for k, v in order.items()])
