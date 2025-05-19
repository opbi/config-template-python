"""Shared Library - File System.

> update at the template repo with unit tests, pull request for review.
"""

from json import dump, load
from os import makedirs, path, remove
from shutil import rmtree


def is_json(path: str) -> bool:
    """Check if the target is json based on the file extension in the path."""
    return path.lower().endswith("json")


def save_json(filepath: str, data: dict | list, sort_keys: bool = False) -> None:
    """Write data to a json file."""
    makedirs(path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        dump(data, file, indent=2, sort_keys=sort_keys)


def read_json(filepath: str) -> dict:
    """Load json data from a file."""
    with open(filepath) as file:
        return load(file)


def check_file(filepath: str) -> bool:
    """Check if a file exists."""
    return path.exists(filepath)


def remove_file(filepath: str) -> None:
    """Remove file at the set path."""
    if path.exists(filepath):
        remove(filepath)


def check_folder(folder_path: str) -> bool:
    """Check if a folder exists."""
    return path.isdir(folder_path)


def remove_folder(folder_path: str) -> None:
    """Remove folder at the set path."""
    if path.exists(folder_path):
        rmtree(folder_path)
