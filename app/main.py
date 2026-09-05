"""Keep macOS or Windows awake by gently nudging the mouse cursor."""

from __future__ import annotations

import argparse
import ctypes
import platform
import threading
import time
from collections.abc import Callable, Sequence


DEFAULT_INTERVAL_SECONDS = 30.0
MOUSE_MOVED_EVENT = 5
HID_EVENT_TAP = 0
LEFT_MOUSE_BUTTON = 0


class Point(ctypes.Structure):
    """A Core Graphics point."""

    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


class WindowsPoint(ctypes.Structure):
    """A Win32 cursor position."""

    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class MacMouse:
    """Small wrapper around the macOS Core Graphics mouse API."""

    def __init__(self) -> None:
        if platform.system() != "Darwin":
            raise RuntimeError("이 프로그램은 현재 macOS에서만 실행할 수 있습니다.")

        self._core_graphics = ctypes.CDLL(
            "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
        )
        self._core_foundation = ctypes.CDLL(
            "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        )
        self._configure_api()

    def _configure_api(self) -> None:
        self._core_graphics.CGEventCreate.argtypes = [ctypes.c_void_p]
        self._core_graphics.CGEventCreate.restype = ctypes.c_void_p
        self._core_graphics.CGEventGetLocation.argtypes = [ctypes.c_void_p]
        self._core_graphics.CGEventGetLocation.restype = Point
        self._core_graphics.CGEventCreateMouseEvent.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            Point,
            ctypes.c_uint32,
        ]
        self._core_graphics.CGEventCreateMouseEvent.restype = ctypes.c_void_p
        self._core_graphics.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        self._core_graphics.CGEventPost.restype = None
        self._core_foundation.CFRelease.argtypes = [ctypes.c_void_p]
        self._core_foundation.CFRelease.restype = None

    def position(self) -> Point:
        event = self._core_graphics.CGEventCreate(None)
        if not event:
            raise RuntimeError("현재 마우스 위치를 읽을 수 없습니다.")
        try:
            return self._core_graphics.CGEventGetLocation(event)
        finally:
            self._core_foundation.CFRelease(event)

    def move_to(self, point: Point) -> None:
        event = self._core_graphics.CGEventCreateMouseEvent(
            None,
            MOUSE_MOVED_EVENT,
            point,
            LEFT_MOUSE_BUTTON,
        )
        if not event:
            raise RuntimeError("마우스 이동 이벤트를 만들 수 없습니다.")
        try:
            self._core_graphics.CGEventPost(HID_EVENT_TAP, event)
        finally:
            self._core_foundation.CFRelease(event)

    def nudge(self) -> None:
        """Move one pixel horizontally, then return to the original position."""
        original = self.position()
        offset = -1.0 if original.x >= 1.0 else 1.0
        self.move_to(Point(original.x + offset, original.y))
        time.sleep(0.05)
        self.move_to(original)


class WindowsMouse:
    """Small wrapper around the Win32 cursor API."""

    def __init__(self) -> None:
        if platform.system() != "Windows":
            raise RuntimeError("이 마우스 구현은 Windows에서만 실행할 수 있습니다.")

        self._user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._user32.GetCursorPos.argtypes = [ctypes.POINTER(WindowsPoint)]
        self._user32.GetCursorPos.restype = ctypes.c_bool
        self._user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
        self._user32.SetCursorPos.restype = ctypes.c_bool

    def position(self) -> WindowsPoint:
        point = WindowsPoint()
        if not self._user32.GetCursorPos(ctypes.byref(point)):
            raise ctypes.WinError(ctypes.get_last_error())
        return point

    def move_to(self, point: WindowsPoint) -> None:
        if not self._user32.SetCursorPos(point.x, point.y):
            raise ctypes.WinError(ctypes.get_last_error())

    def nudge(self) -> None:
        """Move one pixel horizontally, then return to the original position."""
        original = self.position()
        offset = -1 if original.x >= 1 else 1
        self.move_to(WindowsPoint(original.x + offset, original.y))
        time.sleep(0.05)
        self.move_to(original)


def create_mouse() -> MacMouse | WindowsMouse:
    """Create the mouse controller for the current operating system."""
    system = platform.system()
    if system == "Darwin":
        return MacMouse()
    if system == "Windows":
        return WindowsMouse()
    raise RuntimeError("이 프로그램은 macOS와 Windows에서만 실행할 수 있습니다.")


def run(
    interval: float,
    nudge: Callable[[], None],
    stop_event: threading.Event | None = None,
) -> None:
    """Nudge the cursor at each interval until stopped."""
    if interval <= 0:
        raise ValueError("이동 간격은 0보다 커야 합니다.")

    stop_event = stop_event or threading.Event()
    while not stop_event.wait(interval):
        nudge()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="화면 보호기 진입을 막기 위해 마우스를 주기적으로 살짝 움직입니다."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL_SECONDS,
        help="마우스 이동 간격(초, 기본값: 30)",
    )
    args = parser.parse_args(argv)
    if args.interval <= 0:
        parser.error("--interval은 0보다 커야 합니다.")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    mouse = create_mouse()
    print(
        f"실행 중: {args.interval:g}초마다 커서를 움직입니다. "
        "종료하려면 Ctrl+C를 누르세요."
    )
    try:
        run(args.interval, mouse.nudge)
    except KeyboardInterrupt:
        print("\n종료했습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
