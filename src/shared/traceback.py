import traceback
from logging import Formatter

CUSTOM_DECORATOR_NAME = "decorated"  # CONVENTION: in-house decorator name


class TracebackCleaner(Formatter):
    def formatException(self, exc_info):  # noqa: N802 [legit use to align with the Formatter method]
        """Go through the tracebacks and filter out decorator files."""
        exc_type, exc_value, tb = exc_info

        filtered = []

        while tb is not None:
            frame = traceback.extract_tb(tb, limit=1)[0]

            if frame.name != CUSTOM_DECORATOR_NAME:
                filtered.append(frame)

            tb = tb.tb_next

        output = "Traceback (most recent call last except decorators):\n" if len(filtered) else ""
        output += "".join(traceback.format_list(filtered))
        output += "".join(traceback.format_exception_only(exc_type, exc_value))
        return output
