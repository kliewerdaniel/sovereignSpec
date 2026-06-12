from __future__ import annotations

import os
import time
from pathlib import Path
from threading import Event, Thread
from typing import Any, Callable


class FileWatcher:
    """Monitor file changes in watched directories with configurable debounce.

    Fires a callback when any file matching the watched patterns changes.
    Debounces rapid successive changes into a single callback invocation.
    """

    def __init__(
        self,
        root: str | Path,
        watch_dirs: list[str] | None = None,
        debounce_ms: int = 500,
        callback: Callable[[list[Path]], Any] | None = None,
    ):
        self.root = Path(root)
        self.watch_paths = [self.root / d for d in (watch_dirs or ["specs", "adr"])]
        self.watch_paths = [p for p in self.watch_paths if p.exists()]
        if not self.watch_paths:
            self.watch_paths = [self.root]
        self.debounce_seconds = debounce_ms / 1000.0
        self.callback = callback or (lambda _: None)
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._last_snapshot: dict[Path, int] = {}
        self._pending_changes: list[Path] = []
        self._last_fire = 0.0

    def _snapshot(self) -> dict[Path, float]:
        state: dict[Path, float] = {}
        for watch_dir in self.watch_paths:
            if not watch_dir.exists():
                continue
            if watch_dir.is_file():
                state[watch_dir] = watch_dir.stat().st_mtime_ns
            else:
                for f in watch_dir.rglob("*"):
                    if f.is_file() and not f.name.startswith("."):
                        try:
                            state[f] = f.stat().st_mtime_ns
                        except OSError:
                            pass
        return state

    def _poll(self) -> None:
        self._last_snapshot = self._snapshot()
        while not self._stop_event.is_set():
            self._stop_event.wait(max(0.1, self.debounce_seconds / 2))
            if self._stop_event.is_set():
                break

            current = self._snapshot()
            changed = False
            for path, mtime_ns in current.items():
                old = self._last_snapshot.get(path)
                if old is None or mtime_ns != old:
                    if path not in self._pending_changes:
                        self._pending_changes.append(path)
                    changed = True

            removed = set(self._last_snapshot) - set(current)
            for path in removed:
                if path not in self._pending_changes:
                    self._pending_changes.append(path)
                changed = True

            self._last_snapshot = current

            now = time.monotonic()
            if changed and self._pending_changes and (now - self._last_fire) >= self.debounce_seconds:
                to_fire = self._pending_changes[:]
                self._pending_changes.clear()
                self._last_fire = now
                try:
                    self.callback(to_fire)
                except Exception:
                    pass

    def start(self) -> None:
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._poll, daemon=True, name="file-watcher")
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
