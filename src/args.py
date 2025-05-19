"""Package Structure Convention.

cli args specs for running the src module
"""

from argparse import ArgumentParser, Namespace

from .shared.args import validate_args_for_action

ACTION_ARGS = {"get_order": ["order_id"], "get_bill": ["order_data"]}


def parse_args() -> Namespace:
    """Define and return args from cli."""
    parser = ArgumentParser()

    parser.add_argument("action", type=str, choices=["get_order", "get_bill"])

    # IMPORTANT: do not use --id, as it would confuse python -m
    parser.add_argument("--order_id", type=str)
    parser.add_argument("--order_data", type=str, help="output from get_order action.")

    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--upload", type=bool, default=False)

    args, _ = parser.parse_known_args()

    validate_args_for_action(args, ACTION_ARGS)

    return args
