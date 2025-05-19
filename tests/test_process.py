import json
from argparse import Namespace
from os import getenv
from unittest.mock import patch

import pytest

from src.process import get_bill_process, get_order_process, process
from tests.__fixtures__.order import order

mute_print = patch("builtins.print")


@patch("src.process.storage.save_file")
@patch("src.process.file.save_json")
@patch("src.process.get_order", return_value=order)
@mute_print
class TestGetOrderProcess:
    def test_upload(self, _, _get_order, _save_json, _blob_save):
        """Should get data and save file to blob storage and return the filepath."""
        order_id = "1"
        get_order_process(order_id, "output/1.json", upload=True)

        storage_container = getenv("AZURE_STORAGE_CONTAINER_NAME", "")
        storage_path = f"order/{order_id}.json"

        _get_order.assert_called_once_with(order_id)
        assert _blob_save.called
        _save_json.assert_called_once_with(
            "output/1.json",
            {
                "order_id": order_id,
                "order": json.dumps(order),
                "storage_container": storage_container,
                "storage_path": storage_path,
            },
        )

    def test_not_upload(self, _, _get_order, _save_json, _blob_save):
        """Should get data and save file to blob storage and return the filepath."""
        order_id = "1"
        get_order_process(order_id, "output/1.json")

        _get_order.assert_called_once_with(order_id)
        assert not _blob_save.called
        _save_json.assert_called_once_with(
            "output/1.json",
            {"order_id": order_id, "order": json.dumps(order)},
        )


@patch("src.process.storage.save_file")
@patch("src.process.file.save_json")
@mute_print
class TestGetBillProcess:
    order_id = "1"
    storage_container = getenv("AZURE_STORAGE_CONTAINER_NAME", "")
    storage_path = f"bill/{order_id}.txt"
    order_data = json.dumps({"order_id": order_id, "order": order})
    order_storage_path = f"order/{order_id}.json"
    blob_only_data = json.dumps(
        {
            "order_id": order_id,
            "storage_container": storage_container,
            "storage_path": order_storage_path,
        }
    )

    @pytest.mark.online
    def test_blob_only_data(self, _, _save_json, _blob_save):
        """Should get data from blob storage and process the result."""
        get_bill_process(self.blob_only_data, "output/1.json")

        assert not _blob_save.called
        _save_json.assert_called_once_with(
            "output/1.json",
            {"order_id": self.order_id, "bill": 13.4},
        )

    def test_upload(self, _, _save_json, _blob_save):
        """Should get data and save file to blob storage and return the filepath."""
        get_bill_process(self.order_data, "output/1.json", upload=True)

        assert _blob_save.called
        _save_json.assert_called_once_with(
            "output/1.json",
            {
                "order_id": self.order_id,
                "bill": 44.4,
                "storage_container": self.storage_container,
                "storage_path": self.storage_path,
            },
        )

    def test_not_upload(self, _, _save_json, _blob_save):
        """Should get data and save file to blob storage and return the filepath."""
        get_bill_process(self.order_data, "output/1.json")

        assert not _blob_save.called
        _save_json.assert_called_once_with(
            "output/1.json",
            {"order_id": self.order_id, "bill": 44.4},
        )


@pytest.mark.parametrize("action", ["get_order", "get_bill"])
@patch("src.process.get_bill_process")
@patch("src.process.get_order_process")
def test_process(_get_order_process, _get_bill_process, action):
    """Should call the corresponding process based args."""
    order_id = "1"
    order_data = json.dumps({"order_id": "1", "order": order})
    output_file = "output/1.json"
    args = Namespace(
        action=action,
        order_id=order_id,
        order_data=order_data,
        output_file=output_file,
        upload=False,
    )

    process(args)

    if action == "get_order":
        _get_order_process.assert_called_once_with(order_id, output_file, False)
        _get_bill_process.assert_not_called()
    elif action == "get_bill":
        _get_bill_process.assert_called_once_with(order_data, output_file, False)
        _get_order_process.assert_not_called()
