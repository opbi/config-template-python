"""Shared Library - Metrics.

> update at the template repo with unit tests, pull request for review.
"""

import csv
import os

import psutil

from .datetime import timestamp


def process_ram() -> str:
    """Get the RAM usage of current process."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_gb = memory_info.rss / (1024 * 1024 * 1024)
    return f"{memory_gb:.2f}"


def log_metrics(file_path: str, data: list) -> None:
    """Log metrics data as a new role to a csv file."""
    with open(file_path, mode="a", newline="") as file:
        csv.writer(file).writerow([*data, timestamp(), process_ram()])
