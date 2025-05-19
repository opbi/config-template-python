from math import isclose

import pytest

from src.data import MENU
from src.lib.order import total
from tests.__fixtures__.order import order


def zip_map(order):
    """Zip map implementation of total."""
    return sum(map(lambda k, v: MENU[k] * v, *zip(*order.items(), strict=False)))  # noqa: C417


def list_comprehension(order):
    """List comprehension implementation of total."""
    return sum([MENU[k] * v for k, v in order.items()])


def kv_map(order):
    """KV map implementation of total."""
    return sum(map(lambda kv: MENU[kv[0]] * kv[1], order.items()))  # noqa: C417


class TestBenchmarkTotal:
    def test_total(self):
        """Test total."""
        assert isclose(total(order), 44.4)

    @pytest.mark.benchmark()
    def test_zip_map(self, benchmark):
        """Benchmark zip map implementations of total."""
        benchmark(zip_map, order)

    @pytest.mark.benchmark()
    def test_list_comprehension(self, benchmark):
        """Benchmark list comprehension implementation of total."""
        benchmark(list_comprehension, order)

    @pytest.mark.benchmark()
    def test_kv_map(self, benchmark):
        """Benchmark kv map implementation of total."""
        benchmark(kv_map, order)
