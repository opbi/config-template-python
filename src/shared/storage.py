"""Shared Library - Azure Storage.

> update at the template repo with unit tests, pull request for review.
"""

from collections.abc import Callable
from contextlib import suppress
from functools import wraps
from json import dumps, loads
from os import getenv, makedirs, path, walk
from typing import Any

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContainerClient

from .file import is_json
from .retry import retry

ENCODING = "utf-8"

#
# helper functions
#


class BlobServiceManager:
    """Class to encapsulate blob service client cache."""

    _cached_blob_service_client: BlobServiceClient | None = None

    @staticmethod
    def _get_connection_string() -> str:
        """Form connection string from env vars."""
        # NOTE: currently env_vars parsing in production is via --env_vars cli params at process time
        # so make sure to get the env_vars when init the storage instance
        account_name = getenv("AZURE_STORAGE_ACCOUNT_NAME")
        account_key = getenv("AZURE_STORAGE_ACCOUNT_KEY")
        return (
            "DefaultEndpointsProtocol=https;"
            + f"AccountName={account_name};"
            + f"AccountKey={account_key};"
            + "EndpointSuffix=core.windows.net"
        )

    @classmethod
    def get_blob_service_client(cls, cache_client: bool = False) -> BlobServiceClient:
        """Get the container client."""
        if cache_client and cls._cached_blob_service_client:
            blob_service_client = cls._cached_blob_service_client
        else:
            connection_string = cls._get_connection_string()
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            if cache_client:
                cls._cached_blob_service_client = blob_service_client

        return blob_service_client


def with_container_setup_teardown(func: Callable) -> Callable:
    """Decorator to provide abs container_client with teardown for functions."""

    @wraps(func)
    def decorated(*args, container_name=None, create_container=False, cache_client=True, **kwargs):
        blob_service_client = BlobServiceManager.get_blob_service_client(cache_client)

        _container_name = container_name or getenv("AZURE_STORAGE_CONTAINER_NAME", "")
        container_client = blob_service_client.get_container_client(_container_name)

        if create_container:
            with suppress(ResourceExistsError):
                container_client.create_container()

        try:
            return func(container_client, *args, **kwargs)
        finally:
            if not cache_client:
                blob_service_client.close()
                if BlobServiceManager._cached_blob_service_client:
                    BlobServiceManager._cached_blob_service_client = None

    return decorated


#
# file functions
#


@retry()
@with_container_setup_teardown
def save_file(container: ContainerClient, path: str, data: dict | str) -> None:
    """Save data (dict or str) as JSON or text to the Azure Blob Storage container."""
    if not isinstance(data, dict if is_json(path) else str):
        msg = f"Data type {type(data)} doesn't match file type {path}"
        raise TypeError(msg)

    content = dumps(data) if is_json(path) else str(data)
    container.get_blob_client(path).upload_blob(content.encode(ENCODING), overwrite=True)


@with_container_setup_teardown
def read_file(container: ContainerClient, path: str) -> Any:
    """Read file from path on Azure Blob Storage container."""
    content = container.get_blob_client(path).download_blob().readall().decode(ENCODING)
    return loads(content) if is_json(path) else content


@with_container_setup_teardown
def check_file(container: ContainerClient, path: str) -> bool:
    """Check if file exists on Azure Blob Storage container."""
    return container.get_blob_client(path).exists()


@retry()
@with_container_setup_teardown
def upload_file(container: ContainerClient, file_path: str, storage_path: str = "") -> None:
    """Upload file to Azure Blob Storage container path."""
    _storage_path = storage_path or file_path
    try:
        with open(file_path, "rb") as data:
            container.get_blob_client(_storage_path).upload_blob(data, overwrite=True)
    except FileNotFoundError:
        pass


@retry()
@with_container_setup_teardown
def download_file(container: ContainerClient, storage_path: str, file_path: str = "") -> None:
    """Download file from Azure Blob Storage container path."""
    _file_path = file_path or storage_path
    makedirs(path.dirname(_file_path), exist_ok=True)
    with open(_file_path, "wb") as file:
        file.write(container.get_blob_client(storage_path).download_blob().readall())


#
# folder functions
#


@retry()
@with_container_setup_teardown
def upload_folder(_container: ContainerClient, folder_path: str, storage_path: str = "") -> None:
    """Upload local folder dir to Azure Blob Storage container path."""
    for root, _, files in walk(folder_path):
        for file in files:
            upload_file(f"{root}/{file}", f"{storage_path}/{file}" if storage_path else None)


@with_container_setup_teardown
def check_folder(container: ContainerClient, path: str) -> bool:
    """Check if the folder of the path exists on Azure Blob Storage container."""
    return any(container.list_blobs(name_starts_with=path))


@retry()
@with_container_setup_teardown
def download_folder(container: ContainerClient, storage_path: str, folder_root_path: str) -> None:
    """Download folder from Azure Blob Storage container path."""
    for blob in container.list_blobs(name_starts_with=storage_path):
        # blob.name is the full file path on storage
        # use the full path so that nested folders can be downloaded
        in_folder_file_path = blob.name.removeprefix(storage_path)
        file_path = f"{folder_root_path}{in_folder_file_path}"
        download_file(blob.name, file_path)


#
# universal functions
#


@with_container_setup_teardown
def remove(container: ContainerClient, path: str) -> None:
    """Remove file from Azure Blob Storage container."""
    # Check if the path is a folder by listing blobs with the prefix
    blobs = list(container.list_blobs(name_starts_with=path))

    with suppress(ResourceNotFoundError):
        if blobs:
            for blob in blobs:
                container.get_blob_client(blob.name).delete_blob()
        else:
            container.get_blob_client(path).delete_blob()
