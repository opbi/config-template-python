import sys
from argparse import ArgumentParser, Namespace
from os import environ, getenv
from re import escape

import pytest

from src.shared.args import (
    ArgumentMissingError,
    _parse_export_env_vars,
    parse_env_vars,
    validate_args_for_action,
)


class TestParseExportEnvVars:
    def test_semicolon_delimiter(self):
        """Should parse env vars with semicolon delimiter."""
        assert "TEST_ENV_VAR_1" not in environ
        assert "TEST_ENV_VAR_2" not in environ

        env_vars = "TEST_ENV_VAR_1=foo;TEST_ENV_VAR_2=bar;"
        _parse_export_env_vars(env_vars)

        assert environ["TEST_ENV_VAR_1"] == "foo"
        assert environ["TEST_ENV_VAR_2"] == "bar"
        assert getenv("TEST_ENV_VAR_1") == "foo"
        assert getenv("TEST_ENV_VAR_2") == "bar"

        environ.pop("TEST_ENV_VAR_1")
        environ.pop("TEST_ENV_VAR_2")

    def test_newline_delimiter(self):
        """Should parse env vars with newline delimiter."""
        assert "TEST_ENV_VAR_1" not in environ
        assert "TEST_ENV_VAR_2" not in environ

        env_vars = "TEST_ENV_VAR_1=foo\n\nTEST_ENV_VAR_2=bar\n"
        _parse_export_env_vars(env_vars)

        assert environ["TEST_ENV_VAR_1"] == "foo"
        assert environ["TEST_ENV_VAR_2"] == "bar"
        assert getenv("TEST_ENV_VAR_1") == "foo"
        assert getenv("TEST_ENV_VAR_2") == "bar"

        environ.pop("TEST_ENV_VAR_1")
        environ.pop("TEST_ENV_VAR_2")

    def test_string_literal_newline(self):
        """Should parse env vars with newline delimiter in string literal."""
        assert "TEST_ENV_VAR_1" not in environ
        assert "TEST_ENV_VAR_2" not in environ

        env_vars = """
        TEST_ENV_VAR_1=foo
        TEST_ENV_VAR_2=bar
        """

        _parse_export_env_vars(env_vars)

        assert environ["TEST_ENV_VAR_1"] == "foo"
        assert environ["TEST_ENV_VAR_2"] == "bar"
        assert getenv("TEST_ENV_VAR_1") == "foo"
        assert getenv("TEST_ENV_VAR_2") == "bar"

        environ.pop("TEST_ENV_VAR_1")
        environ.pop("TEST_ENV_VAR_2")

    def test_credentials_encoded_with_equal_signs(self):
        """Should parse env vars with newline delimiter in string literal."""
        assert "TEST_ENV_VAR_1" not in environ
        assert "TEST_ENV_VAR_2" not in environ

        env_vars = """
        TEST_ENV_VAR_1=H9s2aPEij+AStawH10g==;TEST_ENV_VAR_2=foo-bar;
        """

        _parse_export_env_vars(env_vars)

        assert environ["TEST_ENV_VAR_1"] == "H9s2aPEij+AStawH10g=="
        assert getenv("TEST_ENV_VAR_1") == "H9s2aPEij+AStawH10g=="
        assert environ["TEST_ENV_VAR_2"] == "foo-bar"

        environ.pop("TEST_ENV_VAR_1")
        environ.pop("TEST_ENV_VAR_2")


class TestParseEnvVars:
    def test_parse_string_input(self):
        """Should parse string from cli and export env vars."""
        assert "TEST_ENV_VAR_1" not in environ
        assert "TEST_ENV_VAR_2" not in environ

        sys.argv = [
            "test_args.py",
            "get_bill",
            "--order_content",
            "example",
            "--output_file",
            "./output",
            "--env_vars",
            "TEST_ENV_VAR_1=test-value-1\nTEST_ENV_VAR_2=RANDOM_VALUE\n",
        ]

        parse_env_vars()

        assert environ["TEST_ENV_VAR_1"] == "test-value-1"
        assert environ["TEST_ENV_VAR_2"] == "RANDOM_VALUE"

        environ.pop("TEST_ENV_VAR_1")
        environ.pop("TEST_ENV_VAR_2")

    def test_parse_string_literal(self):
        """Should parse string from cli and export env vars."""
        assert "TEST_ENV_VAR_1" not in environ
        assert "TEST_ENV_VAR_2" not in environ

        sys.argv = [
            "test_args.py",
            "get_bill",
            "--order_content",
            "example",
            "--output_file",
            "./output",
            "--env_vars",
            """TEST_ENV_VAR_1=test-value-1
            TEST_ENV_VAR_2=RANDOM_VALUE""",
        ]

        parse_env_vars()

        assert environ["TEST_ENV_VAR_1"] == "test-value-1"
        assert environ["TEST_ENV_VAR_2"] == "RANDOM_VALUE"

        environ.pop("TEST_ENV_VAR_1")
        environ.pop("TEST_ENV_VAR_2")


class TestParseKnownArgs:
    def test_parse_missing_args_without_default_value(self):
        """Should have the key with None value."""
        sys.argv = ["test_args.py", "get_order"]

        parser = ArgumentParser()
        parser.add_argument("action", type=str)
        parser.add_argument("--order_id", type=str)
        args, _ = parser.parse_known_args()

        _args = vars(args)
        assert _args["action"] == "get_order"
        assert "order_id" in _args
        assert _args["order_id"] is None
        assert args.order_id is None

    def test_parse_missing_args_with_empty_default_value(self):
        """Should have the key with None value."""
        sys.argv = ["test_args.py", "get_order"]

        parser = ArgumentParser()
        parser.add_argument("action", type=str)
        parser.add_argument("--order_id", type=str, default="")
        args, _ = parser.parse_known_args()

        _args = vars(args)
        assert _args["action"] == "get_order"
        assert "order_id" in _args
        assert _args["order_id"] == ""
        assert not _args["order_id"]
        assert args.order_id == ""
        assert not args.order_id


class TestValidateArgsForAction:
    def test_valid_args(self):
        """Should pass validation for valid args."""
        args = Namespace(
            action="get_order",
            order_id="1",
            input_file=None,
            output_file=None,
        )
        action_args = {
            "get_order": ["order_id"],
        }

        validate_args_for_action(args, action_args)

    def test_missing_args_result(self):
        """Should raise ArgumentMissingError for missing args."""
        args = Namespace(
            action="get_order",
            order_id=None,
            input_file=None,
            output_file=None,
        )
        action_args = {
            "get_order": ["order_id"],
        }

        message = escape("Parameter['order_id'] is required for action<get_order>.")

        with pytest.raises(ArgumentMissingError, match=message):
            validate_args_for_action(args, action_args)

    def test_missing_args_result_with_default_values(self):
        """Should raise ArgumentMissingError for missing args with empty default values."""
        args = Namespace(
            action="get_order",
            order_id="",
            input_file=None,
            output_file=None,
        )
        action_args = {
            "get_order": ["order_id"],
        }

        message = escape("Parameter['order_id'] is required for action<get_order>.")

        with pytest.raises(ArgumentMissingError, match=message):
            validate_args_for_action(args, action_args)

    def test_multiple_missing_args(self):
        """Should raise ArgumentMissingError for multiple missing args."""
        args = Namespace(
            action="get_order",
            order_id="",
            input_file=None,
            output_file="",
        )
        action_args = {
            "get_order": ["order_id", "output_file"],
        }

        message = escape("Parameter['order_id', 'output_file'] is required for action<get_order>.")

        with pytest.raises(ArgumentMissingError, match=message):
            validate_args_for_action(args, action_args)

    def test_empty_array_assertion(self):
        """Should assert empty array as falsy."""
        if []:
            pytest.fail("Empty array should be falsy.")

        if [1]:
            assert True

        if not None:
            assert True

        if not "":
            assert True
