"""A custom progress module.

seamlessly combine tqdm and its fallback in non-interactive tty
- when progress bar is on, tqdm is utilised for its local display optimisation (miniters, miniterval)
- when progress bar is disabled, the update fallback to the logger with format aligned with tqdm
- in both cases, percentage update will be performed and percentage callback will be called if specified

# tqdm.std: https://github.com/tqdm/tqdm/blob/master/tqdm/std.py
"""

import logging
from os import getenv
from sys import stdout

from tqdm import tqdm

TQDM_FORMAT = "{desc}: {n}/{total} {unit} |{bar}| {percentage:.0f}% [{elapsed}<{remaining}, {rate_fmt}]"

logger = logging.getLogger(__name__)


def check_ipynb():
    """Check if in ipynb environment."""
    try:
        import IPython

        if getattr(IPython, "get_ipython", lambda: False)():  # confirm we are in an ipynb kernel
            return True
    except ImportError:
        pass

    return False


def disable_tqdm() -> bool:
    """Check if we need to disable tqdm."""
    reason = None
    if check_ipynb():
        pass
    elif not stdout.isatty():
        reason = "the console is not interactive"
    elif getenv("PROGRESS_DISABLE_TQDM"):
        reason = "PROGRESS_DISABLE_TQDM set"

    if reason:
        logger.info(f"Progress using logging instead of tqdm because {reason}.")
        return True

    return False


class Progress(tqdm):
    """Enhanced tqdm with API updates and improved logging fallback."""

    def __init__(
        self,
        *args,
        desc="",
        no_bar=False,
        percentage_callback=None,
        percentage_interval=10,
        **kwargs,
    ):
        """Initialize enhanced tqdm with additional progress tracking options."""
        self.desc = desc
        self.percentage = 0.0
        self.tqdm_disabled = no_bar or disable_tqdm()

        self.last_callback_percentage = 0.0
        self.percentage_callback = percentage_callback
        self.percentage_interval = percentage_interval

        super().__init__(
            *args,
            disable=self.tqdm_disabled,
            bar_format=TQDM_FORMAT,
            desc=desc,
            **kwargs,
        )

    def _percentage_update_and_callback(self):
        """Fallback function to update progress."""
        self.percentage = self.n / self.total * 100

        if (
            self.percentage_callback
            and self.percentage - self.last_callback_percentage >= self.percentage_interval
        ):
            self.last_callback_percentage = self.percentage
            self.percentage_callback(self.percentage)

    def _log_progress(self):
        """Fallback function to log progress."""
        unit, elapsed = self.format_dict["unit"], self.format_dict["elapsed"]
        rate = elapsed / self.n
        remaining = rate * (self.total - self.n)
        progress_info = (
            f"{self.desc}: {self.n}/{self.total} {unit} {self.percentage:.2f}% "
            f"[{elapsed:.1f}<{remaining:.1f}], {rate:.1f} s/{unit}"
        )
        logger.info(progress_info)

    def __iter__(self):
        """Extend __iter__."""
        for item in super().__iter__():
            # tqdm.__iter__ only update format_dict during iter, and self.n only in the end
            # to use custom percentage callback with or without tqdm, we are updating self.n on iter
            self.n += 1
            self._percentage_update_and_callback()

            if self.tqdm_disabled:
                self._log_progress()

            yield item

    def update(self, delta=1):
        """Extend update method."""
        if self.tqdm_disabled:
            self.n += delta
        else:
            super().update(delta)

        self._percentage_update_and_callback()

        if self.tqdm_disabled:
            self._log_progress()

    def write(self, message, **kwargs):
        """Extend write method."""
        if self.tqdm_disabled:
            logger.info(message)
        else:
            super().write(message, **kwargs)


def progress(*args, **kwargs):
    """Custom progress."""
    return Progress(*args, **kwargs)
