import threading
import time
from typing import Callable


class Timer:
    def __init__(self, callback: Callable[[float], None] = None):
        self._elapsed = 0.0
        self._running = False
        self._paused = False
        self._thread: threading.Thread = None
        self._lock = threading.Lock()
        self._callback = callback
        self._start_time = 0.0

    def _run(self):
        self._start_time = time.time()
        while self._running:
            if not self._paused:
                with self._lock:
                    self._elapsed = time.time() - self._start_time
                if self._callback:
                    self._callback(self._elapsed)
            else:
                self._start_time = time.time() - self._elapsed
            time.sleep(0.05)

    def start(self):
        if not self._running:
            self._running = True
            self._paused = False
            self._elapsed = 0.0
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def pause(self):
        with self._lock:
            self._paused = True

    def resume(self):
        with self._lock:
            self._paused = False
            self._start_time = time.time() - self._elapsed

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def get_elapsed(self) -> float:
        with self._lock:
            return self._elapsed

    def reset(self):
        with self._lock:
            self._elapsed = 0.0
            self._running = False
            self._paused = False

    @staticmethod
    def format_time(seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 100)
        return f'{mins:02d}:{secs:02d}.{ms:02d}'
