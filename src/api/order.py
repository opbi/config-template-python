from src.data import ORDERS
from src.shared.logger import with_logger
from src.types import Order


@with_logger()
def get_order(order_id: str) -> Order:
    """Dummy api for example."""
    return ORDERS[order_id]
