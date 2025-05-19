"""Shared Library - Retry.

> update at the template repo with unit tests, pull request for review.
"""

from collections.abc import Callable
from functools import wraps
from time import sleep
from typing import Any

from .logger import logger


def retry(
    max_attempts: int = 3,
    delay: int = 5,
    skip: Callable[[Exception], bool] | None = None,
    suppress: Callable[[Exception], bool] | None = None,
) -> Callable:
    """Decorator that retries a function a specified number of times with a delay between each attempt.

    Args:
        max_attempts (int): The maximum number of attempts to make.
        delay (int): The delay in seconds between each attempt.
        skip (Callable: e -> bool): the conditional error to be skipped
        suppress (Callable: e -> bool): the conditional error to be suppressed

    Returns:
        function: The decorated function.

    Raises:
        Exception: If the function fails after the maximum number of attempts.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            attempts: int = 0

            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:  # noqa: PERF203 [legit use of try-except in a loop]
                    if skip and skip(e):
                        logger.info(f"Skip exception: {e}")
                        break

                    logger.debug(f"{func.__name__} > attempt {attempts + 1} failed")
                    attempts += 1

                    if attempts == max_attempts:
                        if suppress and suppress(e):
                            logger.info(f"Suppress exception: {e}")
                            break

                        raise

                    sleep(delay)

            return None

        return decorated

    return decorator
