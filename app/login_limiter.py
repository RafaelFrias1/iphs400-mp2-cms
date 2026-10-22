"""Refuses logins for an email after too many failures (ADR-006)."""
from __future__ import annotations

import threading
import time
from typing import Callable

from app.accounts import normalize_email

MAX_FAILURES = 5
WINDOW = 15 * 60  # seconds: failures count within it, and a lockout lasts it
LOCK_STRIPES = 64  # a fixed set of locks, so they never pile up in memory


class LoginLimiter:
    """Remembers recent failed logins per typed email, in memory.

    After MAX_FAILURES within WINDOW, the email is locked out for WINDOW.
    `clock` is swappable so tests can freeze and advance time.
    Callers hold `lock(email)` across the check, the password verify and the
    recording, so simultaneous guesses cannot all slip past the check.
    """

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self.clock = clock
        self._locks = [threading.Lock() for _ in range(LOCK_STRIPES)]
        self._state = threading.Lock()  # guards the two dicts; pruning spans emails
        self._failures: dict[str, list[float]] = {}
        self._locked_until: dict[str, float] = {}

    def lock(self, email: str) -> threading.Lock:
        return self._locks[hash(_key(email)) % LOCK_STRIPES]

    def seconds_locked(self, email: str) -> float:
        """How long this email's lockout has left; 0 when it is not locked out."""
        with self._state:
            until = self._locked_until.get(_key(email), float("-inf"))
        return max(0.0, until - self.clock())

    def record_failure(self, email: str) -> None:
        key, now = _key(email), self.clock()
        with self._state:
            self._prune(now)
            recent = [t for t in self._failures.get(key, []) if now - t < WINDOW]
            recent.append(now)
            if len(recent) >= MAX_FAILURES:
                self._locked_until[key] = now + WINDOW
                self._failures.pop(key, None)
            else:
                self._failures[key] = recent

    def clear(self, email: str) -> None:
        """Forget an email's failures, after it logs in successfully."""
        with self._state:
            self._failures.pop(_key(email), None)

    def _prune(self, now: float) -> None:
        """Forget failures and lockouts that no longer count, so typed emails
        that never come back do not pile up in memory."""
        for key, times in list(self._failures.items()):
            if now - times[-1] >= WINDOW:
                del self._failures[key]
        for key, until in list(self._locked_until.items()):
            if until <= now:
                del self._locked_until[key]

    def reset(self) -> None:
        with self._state:
            self._failures.clear()
            self._locked_until.clear()


def _key(email: str) -> str:
    return normalize_email(email)


limiter = LoginLimiter()
