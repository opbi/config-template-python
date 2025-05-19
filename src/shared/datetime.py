"""Shared Library - Datetime.

> update at the template repo with unit tests, pull request for review.
"""

from datetime import datetime, timezone

YEAR_TO_SECOND = "%Y-%m-%d %H:%M:%S"


def timestamp():
    """Datetime now with timezone and precision only to s."""
    return datetime.now(tz=timezone.utc).strftime(YEAR_TO_SECOND)


def now():
    """Use UTC timezone by default."""
    return datetime.now(tz=timezone.utc)


def fromtimestamp(timestamp):
    """Convert timestamp to datetime, use utc timezone."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
