import logging
from io import StringIO
from unittest.mock import Mock, patch

import pytest

from src.shared.progress import disable_tqdm, progress


@pytest.mark.skipif(disable_tqdm(), reason="doesn't fully support tqdm.")
class TestAsTQDM:
    def test_use_on_iterator(self):
        """Should work."""
        stderr = StringIO()

        callback = Mock()

        for _ in progress(
            range(10),
            ascii=True,
            file=stderr,
            desc="Testing",
            percentage_callback=callback,
            percentage_interval=20,
        ):
            pass

        _stderr = stderr.getvalue()
        assert "Testing: 10/10 it" in _stderr
        assert "|####" in _stderr
        assert "####|" in _stderr
        assert "100%" in _stderr

        assert callback.call_count == 5

    def test_use_as_context(self):
        """Should work."""
        stdout, stderr = StringIO(), StringIO()

        callback = Mock()

        with progress(
            total=10,
            ascii=True,
            file=stderr,
            desc="Testing",
            percentage_callback=callback,
            percentage_interval=20,
        ) as p:
            for i in range(10):
                p.update(1)
                p.write(str(i), file=stdout)

        _stderr = stderr.getvalue()
        assert "Testing: 10/10 it" in _stderr
        assert "|####" in _stderr
        assert "####|" in _stderr
        assert "100%" in _stderr

        assert "3\n" in stdout.getvalue()

        assert callback.call_count == 5


@patch("src.shared.progress.disable_tqdm", return_value=True)
class TestFallback:
    def test_use_on_iterator(self, _, caplog):
        """Should work."""
        stderr = StringIO()

        callback = Mock()

        with caplog.at_level(logging.INFO):
            for _ in progress(
                range(10),
                file=stderr,
                desc="Testing",
                percentage_callback=callback,
                percentage_interval=20,
            ):
                pass

        assert not stderr.getvalue()
        assert "Testing: 3/10" in caplog.text
        assert "100.00%" in caplog.text
        assert "110.00%" not in caplog.text

        assert callback.call_count == 5

    def test_use_as_context(self, _, caplog):
        """Should work."""
        stderr = StringIO()

        callback = Mock()

        with (
            caplog.at_level(logging.INFO),
            progress(
                total=10,
                file=stderr,
                desc="Testing",
                percentage_callback=callback,
                percentage_interval=20,
            ) as p,
        ):
            for i in range(10):
                p.update(1)
                p.write(f"Message {i}")

        assert not stderr.getvalue()
        assert "Testing: 3/10" in caplog.text
        assert "Message 3" in caplog.text
        assert "100.00%" in caplog.text
        assert "110.00%" not in caplog.text

        assert callback.call_count == 5
