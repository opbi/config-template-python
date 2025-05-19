import json
from subprocess import run

import pytest

from src.data import ORDERS


@pytest.mark.online
class TestMain:
    def test_get_order(self):
        """Should output the file path."""
        res = run(
            [
                "python",
                "-m",
                "src",
                "get_order",
                "--order_id",
                "1",
                "--output_file",
                "./output/order.json",
                "--upload",
                "True",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert "get_order for order 1: {'lamb': 1, 'beef': 1}" in res.stderr
        assert "file saved on /order/1.json" in res.stderr
        assert "pipeline output saved to file: ./output/order.json" in res.stderr

    def test_get_bill(self):
        """Should output the filepath."""
        res = run(
            [
                "python",
                "-m",
                "src",
                "get_bill",
                "--order_data",
                json.dumps({"order_id": "1", "order": ORDERS["1"]}),
                "--output_file",
                "./output/bill.json",
                "--upload",
                "True",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert "get_bill for order 1 - {'lamb': 1, 'beef': 1}: £13.4." in res.stderr
        assert "file saved on /bill/1.txt" in res.stderr
        assert "pipeline output_file saved to file: ./output/bill.json" in res.stderr
