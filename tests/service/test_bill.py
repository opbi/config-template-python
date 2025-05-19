from src.service.bill import get_bill
from tests.__fixtures__.order import order


def test_get_bill():
    """Test get bill."""
    assert get_bill(order) == 44.4
