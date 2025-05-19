"""Shared Library - Args.

> update at the template repo with unit tests, pull request for review.
"""

from argparse import ArgumentParser, Namespace
from os import environ, linesep


def _parse_export_env_vars(env_vars: str) -> None:
    """Parse env_vars string using ; or linesep as delimiter and export them to environ."""
    delimiter = ";" if ";" in env_vars else linesep
    for _pair in env_vars.split(delimiter):
        pair = _pair.strip()
        if pair:  # in case of empty lines
            k, v = pair.split("=", 1)
            environ[k] = v


def parse_env_vars() -> None:
    """Support passing --env_vars='FOO=1;BAR=2' from cli args."""
    parser = ArgumentParser()
    parser.add_argument("--env_vars", type=str)

    args, _ = parser.parse_known_args()

    if args.env_vars:
        _parse_export_env_vars(args.env_vars)


class ArgumentMissingError(Exception):
    def __init__(self, missing: list[str], action: str):
        super().__init__(f"Parameter{missing} is required for action<{action}>.")


def validate_args_for_action(parsed: Namespace, required: dict) -> None:
    """Check if all required arguments are passed for the action."""
    _parsed = vars(parsed)
    action = _parsed["action"]
    missing = [arg for arg in required[action] if arg not in _parsed or not _parsed[arg]]
    if missing:
        raise ArgumentMissingError(missing, action)
