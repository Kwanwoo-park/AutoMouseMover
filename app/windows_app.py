"""Windows desktop UI for AutoMouseMover."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.main import DEFAULT_INTERVAL_SECONDS, WindowsMouse


MAX_INTERVAL_SECONDS = 86_400.0
MAX_DURATION_MINUTES = 525_600


def parse_settings(interval_text: str, duration_text: str) -> tuple[float, int]:
    """Validate values entered in the Windows application."""
    try:
        interval = float(interval_text.strip())
    except ValueError as exception:
        raise ValueError("이동 간격에는 숫자를 입력해 주세요.") from exception

    if interval <= 0 or interval > MAX_INTERVAL_SECONDS:
        raise ValueError("이동 간격은 0초보다 크고 86,400초 이하여야 합니다.")

    normalized_duration = duration_text.strip()
    if not normalized_duration.isdigit():
        raise ValueError("실행 시간에는 0 이상의 정수를 입력해 주세요.")

    duration = int(normalized_duration)
    if duration > MAX_DURATION_MINUTES:
        raise ValueError("실행 시간은 525,600분 이하여야 합니다.")
    return interval, duration


class AutoMouseMoverWindow:
    """Tk based controller for starting and stopping cursor nudges."""

    def __init__(self, root: tk.Tk, mouse: WindowsMouse) -> None:
        self.root = root
        self.mouse = mouse
        self.interval_seconds = DEFAULT_INTERVAL_SECONDS
        self.running = False
        self.move_job: str | None = None
        self.stop_job: str | None = None

        self.interval_value = tk.StringVar(value=f"{DEFAULT_INTERVAL_SECONDS:g}")
        self.duration_value = tk.StringVar(value="0")
        self.status_value = tk.StringVar(value="설정을 확인한 뒤 시작해 주세요.")

        self._build_window()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _build_window(self) -> None:
        self.root.title("AutoMouseMover")
        self.root.resizable(False, False)

        container = ttk.Frame(self.root, padding=24)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(1, weight=1)

        title = ttk.Label(container, text="화면 보호기 방지", font=("맑은 고딕", 17, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 18))

        ttk.Label(container, text="이동 간격").grid(row=1, column=0, sticky="w", pady=6)
        interval_entry = ttk.Entry(container, width=12, textvariable=self.interval_value, justify="right")
        interval_entry.grid(row=1, column=1, sticky="ew", padx=(14, 8), pady=6)
        ttk.Label(container, text="초").grid(row=1, column=2, sticky="w", pady=6)

        ttk.Label(container, text="실행 시간").grid(row=2, column=0, sticky="w", pady=6)
        duration_entry = ttk.Entry(container, width=12, textvariable=self.duration_value, justify="right")
        duration_entry.grid(row=2, column=1, sticky="ew", padx=(14, 8), pady=6)
        ttk.Label(container, text="분 (0 = 무제한)").grid(row=2, column=2, sticky="w", pady=6)

        ttk.Separator(container).grid(row=3, column=0, columnspan=3, sticky="ew", pady=16)
        status = ttk.Label(container, textvariable=self.status_value, anchor="center", justify="center")
        status.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 18))

        button_row = ttk.Frame(container)
        button_row.grid(row=5, column=0, columnspan=3, sticky="ew")
        for column in range(3):
            button_row.columnconfigure(column, weight=1)

        ttk.Button(button_row, text="시작 / 재시작", command=self.start).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(button_row, text="일시 중지", command=self.pause).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(button_row, text="종료", command=self.close).grid(row=0, column=2, sticky="ew", padx=(6, 0))

        interval_entry.focus_set()

    def start(self) -> None:
        try:
            interval, duration = parse_settings(self.interval_value.get(), self.duration_value.get())
        except ValueError as exception:
            messagebox.showerror("설정 오류", str(exception), parent=self.root)
            return

        self._cancel_jobs()
        self.interval_seconds = interval
        self.running = True
        duration_text = "수동 종료 전까지" if duration == 0 else f"{duration}분 동안"
        self.status_value.set(f"실행 중 · {interval:g}초마다 이동 · {duration_text}")
        self._move_cursor()
        if duration > 0:
            self.stop_job = self.root.after(duration * 60_000, self._duration_reached)

    def pause(self) -> None:
        self.running = False
        self._cancel_jobs()
        self.status_value.set("일시 중지됨")

    def _move_cursor(self) -> None:
        if not self.running:
            return
        try:
            self.mouse.nudge()
        except OSError as exception:
            self.running = False
            self._cancel_jobs()
            self.status_value.set("마우스를 움직일 수 없습니다.")
            messagebox.showerror("실행 오류", str(exception), parent=self.root)
            return
        self.move_job = self.root.after(round(self.interval_seconds * 1_000), self._move_cursor)

    def _duration_reached(self) -> None:
        self.running = False
        self._cancel_jobs()
        self.status_value.set("설정한 실행 시간이 지나 자동 중지됨")

    def _cancel_jobs(self) -> None:
        for job in (self.move_job, self.stop_job):
            if job is not None:
                try:
                    self.root.after_cancel(job)
                except tk.TclError:
                    pass
        self.move_job = None
        self.stop_job = None

    def close(self) -> None:
        self.running = False
        self._cancel_jobs()
        self.root.destroy()


def main() -> int:
    root = tk.Tk()
    try:
        mouse = WindowsMouse()
    except (OSError, RuntimeError) as exception:
        root.withdraw()
        messagebox.showerror("AutoMouseMover", str(exception), parent=root)
        root.destroy()
        return 1

    AutoMouseMoverWindow(root, mouse)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
