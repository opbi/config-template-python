import pytest

from src.api.order import get_order
from src.data import ORDERS


class TestGetOrder:
    def test_get_order_with_id(self):
        """Should return order based on the id."""
        assert get_order("1") == ORDERS["1"]
        assert get_order("2") == ORDERS["2"]
        assert get_order("3") == ORDERS["3"]

    def test_get_order_with_invalid_id(self):
        """Should raise KeyError when the id is invalid."""
        with pytest.raises(KeyError):
            get_order("invalid-id")
