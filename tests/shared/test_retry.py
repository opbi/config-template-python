from unittest.mock import Mock, patch

import pytest

from src.shared.retry import retry


@patch("src.shared.retry.sleep")
@patch("src.shared.retry.print")
class TestRetry:
    def test_successful_execution(self, *_):
        """Should succeed without retry."""
        mock_function = Mock(return_value="Success")

        @retry()
        def successful_function():
            return mock_function()

        assert successful_function() == "Success"
        assert mock_function.call_count == 1

    def test_always_fail_execution(self, *_):
        """Should succeed without retry."""
        mock_function = Mock(side_effect=Exception("Internal Error"))

        @retry(delay=0)
        def always_fail_function():
            return mock_function()

        with pytest.raises(Exception, match="Internal Error"):
            always_fail_function()
        assert mock_function.call_count == 3

    def test_fallible_execution(self, *_):
        """Should succeed without retry."""
        mock_function = Mock(side_effect=[Exception("Internal Error"), "Success"])

        @retry(delay=0)
        def fallible_function():
            return mock_function()

        assert fallible_function() == "Success"
        assert mock_function.call_count == 2

    def test_skip_error(self, *_):
        """Should ignore error set in condition."""
        mock_function = Mock(side_effect=Exception("Internal Error"))

        @retry(skip=lambda e: "Internal Error" in str(e))
        def ignored_fail_execution():
            return mock_function()

        assert ignored_fail_execution() is None
        assert mock_function.call_count == 1

    def test_suppress_error(self, *_):
        """Should ignore error set in condition."""
        mock_function = Mock(side_effect=Exception("Internal Error"))

        @retry(suppress=lambda e: "Internal Error" in str(e))
        def ignored_fail_execution():
            return mock_function()

        assert ignored_fail_execution() is None
        assert mock_function.call_count == 3
