import logging
from io import StringIO
from unittest.mock import Mock

from src.shared.logger import logger, with_logger
from src.shared.retry import retry
from src.shared.traceback import TracebackCleaner

log = StringIO()
handler = logging.StreamHandler(log)
handler.setFormatter(TracebackCleaner())
logger.addHandler(handler)


class TestWithLogger:
    def test_parent_children(self, caplog):
        """Should reflect the call structure of parent and children."""

        @with_logger()
        def a():
            return "a"

        @with_logger()
        def b():
            return "b"

        @with_logger()
        def parent():
            return a() + b()

        with caplog.at_level(logging.DEBUG):
            result = parent()
            assert result == "ab"
            assert len(caplog.records) == 6
            assert caplog.records[0].message == "parent > start"
            assert caplog.records[1].message == "parent.a > start"
            assert caplog.records[2].message == "parent.a > finish"
            assert caplog.records[3].message == "parent.b > start"
            assert caplog.records[4].message == "parent.b > finish"
            assert caplog.records[5].message == "parent > finish"

    def test_nested_calls(self, caplog):
        """Should reflect the call structure of parent and children."""

        @with_logger()
        def a():
            return "a"

        @with_logger()
        def b():
            return a()

        @with_logger()
        def c():
            return b()

        with caplog.at_level(logging.DEBUG):
            result = c()
            assert result == "a"
            assert len(caplog.records) == 6
            assert caplog.records[0].message == "c > start"
            assert caplog.records[1].message == "c.b > start"
            assert caplog.records[2].message == "c.b.a > start"
            assert caplog.records[3].message == "c.b.a > finish"
            assert caplog.records[4].message == "c.b > finish"
            assert caplog.records[5].message == "c > finish"

    def test_exception_log(self, caplog):
        """Should log exception."""

        @with_logger()
        def foo(fail, value=3):
            if fail:
                raise Exception("Something is wrong.")  # noqa: EM101, TRY002, TRY003
            return value

        with caplog.at_level(logging.DEBUG):
            try:
                foo(True, value=5)
            except Exception:
                assert len(caplog.records) == 2
                assert caplog.records[0].message == "foo > start"
                assert "True" in caplog.records[1].message
                assert "'value': 5" in caplog.records[1].message


class TestWithRetry:
    def test_success(self, caplog):
        """Should be compatible with other in-house decorators."""

        @with_logger()
        @retry()
        def foo():
            return "foo"

        with caplog.at_level(logging.DEBUG):
            result = foo()
            assert result == "foo"
            assert len(caplog.records) == 2
            assert caplog.records[0].message == "foo > start"
            assert caplog.records[1].message == "foo > finish"

    def test_failed_once(self, caplog):
        """Should log retry depends on the order."""
        mock_function = Mock(side_effect=[Exception("Mock Error"), "Success"])

        @with_logger()
        @retry(delay=0)
        def fallible_function():
            return mock_function()

        with caplog.at_level(logging.DEBUG):
            result = fallible_function()

            assert result == "Success"

            assert len(caplog.records) == 3
            assert caplog.records[0].message == "fallible_function > start"
            assert caplog.records[1].message == "fallible_function > attempt 1 failed"
            assert caplog.records[2].message == "fallible_function > finish"

    def test_failed(self, caplog):
        """Should log retry depends on the order."""

        @with_logger()
        @retry(delay=0)
        def always_fail_function():
            raise ValueError

        with caplog.at_level(logging.DEBUG):
            try:
                always_fail_function()
            except Exception:
                assert len(caplog.records) == 5
                assert caplog.records[0].message == "always_fail_function > start"
                assert caplog.records[1].message == "always_fail_function > attempt 1 failed"
                assert caplog.records[2].message == "always_fail_function > attempt 2 failed"
                assert caplog.records[3].message == "always_fail_function > attempt 3 failed"
                assert caplog.records[4].message == "always_fail_function > error, with args=(), kwargs={}"
                assert "test_logger.py" in caplog.text
                assert "shared/retry.py" not in caplog.text
                assert "shared/logger.py" not in caplog.text
