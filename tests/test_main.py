import threading
import unittest
from unittest.mock import Mock

from app.main import DEFAULT_INTERVAL_SECONDS, parse_args, run


class AutoMoverTest(unittest.TestCase):
    def test_default_interval_is_30_seconds(self) -> None:
        self.assertEqual(parse_args([]).interval, DEFAULT_INTERVAL_SECONDS)

    def test_custom_interval(self) -> None:
        self.assertEqual(parse_args(["--interval", "10"]).interval, 10.0)

    def test_run_nudges_after_interval(self) -> None:
        stop_event = Mock(spec=threading.Event)
        stop_event.wait.side_effect = [False, True]
        nudge = Mock()

        run(30, nudge, stop_event)

        nudge.assert_called_once_with()
        self.assertEqual(stop_event.wait.call_count, 2)
        stop_event.wait.assert_called_with(30)

    def test_run_rejects_non_positive_interval(self) -> None:
        with self.assertRaises(ValueError):
            run(0, Mock())


if __name__ == "__main__":
    unittest.main()
