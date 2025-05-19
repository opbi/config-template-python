import json
from os import getenv
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.validators import OrderData
from tests.__fixtures__.order import order

order_id = "1"
storage_container = getenv("AZURE_STORAGE_CONTAINER_NAME", "")
storage_path = f"order/{order_id}.json"

order_data = json.dumps({"order_id": order_id, "order": order})
nested_order_data = json.dumps({"order_id": order_id, "order": json.dumps(order)})
blob_only_data = json.dumps(
    {
        "order_id": order_id,
        "storage_container": storage_container,
        "storage_path": storage_path,
    }
)


class TestOrderData:
    def test_missing_data(self):
        """Should throw an error if order is missing and no storage_path is available."""
        with pytest.raises(ValidationError):
            OrderData.model_validate_json(json.dumps({"order_id": "1"}))

    def test_nested_serialized_order(self):
        """Should parse nested serialized order data."""
        data = OrderData.model_validate_json(nested_order_data)
        assert data.order == order

    @patch("src.validators.storage.read_file", return_value=order)
    def test_order_with_blob_fallback(self, _storage_read):
        """Should fallback to read order data from blob storage.

        If order data is missing and storage_container and storage_path are available.
        """
        data = OrderData.model_validate_json(blob_only_data)

        _storage_read.assert_called_once_with(storage_path, container_name="config-template-python")
        assert data.order == order
