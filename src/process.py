"""Package Structure Convention.

main process
"""

import json
from argparse import Namespace
from os import getenv

from src.shared import file, storage

from .api.order import get_order
from .service.bill import get_bill
from .shared.logger import logger
from .validators import OrderData


def _upload(data: dict | str, path: str, output: dict) -> None:
    """Helper function to save the data to the storage."""
    storage.save_file(path, data)

    storage_account = getenv("AZURE_STORAGE_ACCOUNT_NAME")
    storage_container = getenv("AZURE_STORAGE_CONTAINER_NAME")
    output["storage_container"] = storage_container
    output["storage_path"] = path
    logger.info(f"file saved on {storage_account}/{storage_container}/{output['storage_path']}")


def get_order_process(order_id: str, output_file: str, upload: bool = False) -> None:
    """Get the order data of order_id and log output to file."""
    order = get_order(order_id)
    logger.info(f"get_order for order {order_id}: {order}.")

    output = {"order_id": order_id, "order": json.dumps(order)}

    if upload:
        _upload(order, f"order/{order_id}.json", output)

    file.save_json(output_file, output)
    logger.info(f"pipeline output saved to file: {output_file}")


def get_bill_process(order_data: str, output_file: str, upload: bool = False) -> None:
    """Get the bill of the given order and log output to file."""
    data = OrderData.model_validate_json(order_data)
    order_id, order = data.order_id, data.order

    bill = get_bill(order)
    logger.info(f"get_bill for order {order_id} - {order}: £{bill}.")

    output = {"order_id": order_id, "bill": bill}

    if upload:
        _upload(f"£{bill}", f"bill/{order_id}.txt", output)

    file.save_json(output_file, output)
    logger.info(f"pipeline output_file saved to file: {output_file}")


def process(args: Namespace) -> None:
    """Main process taking actions of get_order or get_bill."""
    if args.action == "get_order":
        return get_order_process(args.order_id, args.output_file, args.upload)
    return get_bill_process(args.order_data, args.output_file, args.upload)
