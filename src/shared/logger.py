import logging
from collections.abc import Callable
from functools import wraps
from os import getenv
from threading import local

from .traceback import TracebackCleaner

logger = logging.getLogger()
tracing = local()


def config_logger():
    """Configure logging."""
    log_level = getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setFormatter(TracebackCleaner())
    logger.addHandler(handler)
    logger.propagate = False


def with_logger() -> Callable:
    """A decorator that logs function calls."""

    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if not hasattr(tracing, "stack"):
                tracing.stack = []
                tracing.root = func.__name__

            tracing.stack.append(func.__name__)
            call_chain = ".".join(tracing.stack) + " >"

            try:
                logger.debug(f"{call_chain} start")
                result = func(*args, **kwargs)
                logger.debug(f"{call_chain} finish")
            except Exception:
                logger.exception(f"{call_chain} error, with args={args!r}, kwargs={kwargs!r}")
                raise
            else:
                return result
            finally:
                tracing.stack.pop()

        return decorated

    return decorator
