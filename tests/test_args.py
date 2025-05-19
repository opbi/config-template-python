import sys

import pytest

from src.args import parse_args
from src.shared.args import ArgumentMissingError


def test_parse_args_with_extra_args():
    """Should not throw any error."""
    sys.argv = [
        "test_args.py",
        "get_order",
        "--order_id",
        "1",
        "--output_file",
        "./output/1.json",
        "--env_vars",
        "TEST_ENV_VAR_1=test-value-1\nTEST_ENV_VAR_2=RANDOM_VALUES\n",
        "--unknown_args",
        "SOME-VALUE",
    ]

    parse_args()


def test_without_output_file(capsys):
    """Should throw an error."""
    sys.argv = [
        "test_args.py",
        "get_order",
        "--order_id",
        "1",
    ]

    with pytest.raises(SystemExit):
        parse_args()

    err = capsys.readouterr().err

    assert "the following arguments are required: --output_file" in err


class TestParseArgsForGetOrder:
    def test_with_id(self):
        """Should be fine without input_file and output_file."""
        sys.argv = [
            "test_args.py",
            "get_order",
            "--order_id",
            "1",
            "--output_file",
            "./output/1.json",
        ]

        args = parse_args()

        assert args.action == "get_order"
        assert args.order_id == "1"
        assert args.order_data is None
        assert args.output_file == "./output/1.json"
        assert args.upload is False

    def test_without_id(self):
        """Should raise ArgumentMissingError."""
        sys.argv = ["test_args.py", "get_order", "--output_file", "./output"]

        with pytest.raises(ArgumentMissingError):
            parse_args()


class TestParseArgsForGetBill:
    def test_with_order_data(self):
        """Should be fine without id and output_file."""
        sys.argv = [
            "test_args.py",
            "get_bill",
            "--order_data",
            "{'example':'content'}",
            "--output_file",
            "./output/1.json",
        ]

        args = parse_args()

        assert args.action == "get_bill"
        assert args.order_id is None
        assert args.order_data == "{'example':'content'}"
        assert args.output_file == "./output/1.json"
        assert args.upload is False

    def test_without_order_data(self):
        """Should raise ArgumentMissingError."""
        sys.argv = ["test_args.py", "get_bill", "--output_file", "./output"]

        with pytest.raises(ArgumentMissingError):
            parse_args()
