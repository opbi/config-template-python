from typing import Any

from requests import request as _request


def request(url: str, method: str, **kwargs: Any) -> Any:
    """Custom request utility for standardised error handling and logging."""
    kwargs.setdefault("timeout", 30)

    res = _request(url=url, method=method, **kwargs)  # noqa: S113 (legit: timeout set in kwargs)

    res.raise_for_status()

    try:
        return res.json()
    except ValueError:
        return res.text
