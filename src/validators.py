"""Template Only."""

import json
from typing import Any

from pydantic import BaseModel, field_validator, model_validator

from .shared import storage
from .types import Order


class OrderData(BaseModel):
    order_id: str
    order: Order
    storage_container: str | None = None
    storage_path: str | None = None

    @model_validator(mode="before")
    @classmethod
    def order_with_blob_fallback(cls, data: Any) -> Any:
        """If order is not provided, try to read from storage_path."""
        if not data.get("order") and data.get("storage_container") and data.get("storage_path"):
            order = storage.read_file(data.get("storage_path"), container_name=data.get("storage_container"))
            return {**data, "order": order}

        return data

    @field_validator("order", mode="before")
    @classmethod
    def parse_order(cls, v: str | dict) -> dict:
        """Parse order to json if it is str from a nested order_data json."""
        return json.loads(v) if isinstance(v, str) else v
