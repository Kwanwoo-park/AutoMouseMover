import threading
import unittest
from unittest.mock import Mock, patch

from app.main import DEFAULT_INTERVAL_SECONDS, create_mouse, parse_args, run
from app.windows_app import parse_settings


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

    @patch("app.main.WindowsMouse")
    @patch("app.main.platform.system", return_value="Windows")
    def test_create_mouse_uses_windows_api(self, _system: Mock, windows_mouse: Mock) -> None:
        self.assertIs(create_mouse(), windows_mouse.return_value)

    @patch("app.main.MacMouse")
    @patch("app.main.platform.system", return_value="Darwin")
    def test_create_mouse_uses_macos_api(self, _system: Mock, mac_mouse: Mock) -> None:
        self.assertIs(create_mouse(), mac_mouse.return_value)

    @patch("app.main.platform.system", return_value="Linux")
    def test_create_mouse_rejects_unsupported_system(self, _system: Mock) -> None:
        with self.assertRaises(RuntimeError):
            create_mouse()

    def test_windows_settings(self) -> None:
        self.assertEqual(parse_settings("10", "30"), (10.0, 30))
        self.assertEqual(parse_settings("0.5", "0"), (0.5, 0))

    def test_windows_settings_reject_invalid_values(self) -> None:
        for interval, duration in (("0", "0"), ("abc", "0"), ("30", "-1")):
            with self.subTest(interval=interval, duration=duration):
                with self.assertRaises(ValueError):
                    parse_settings(interval, duration)


if __name__ == "__main__":
    unittest.main()
