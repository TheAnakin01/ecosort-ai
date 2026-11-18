"""A small per-client limit on scans, so one caller cannot flood the server.

In memory and per process: fine for the single small instance this runs on.
Several workers or instances would each keep their own count.
"""

import threading
import time
from collections import deque

from fastapi import Request

from . import config


class RateLimiter:
    """Sliding window: at most `limit` requests per client in `window` seconds."""

    def __init__(self, limit: int, window: float = 60.0, max_clients: int = 10_000) -> None:
        self.limit = limit
        self.window = window
        self.max_clients = max_clients
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, now: float | None = None) -> float | None:
        """Record a request. Returns None if allowed, else seconds until a slot frees up."""
        if self.limit <= 0:
            return None
        now = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits.get(key)
            if hits is None:
                if len(self._hits) >= self.max_clients:
                    self._forget_idle(now)
                hits = self._hits[key] = deque()
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return max(self.window - (now - hits[0]), 0.0)
            hits.append(now)
            return None

    def _forget_idle(self, now: float) -> None:
        idle = [k for k, h in self._hits.items() if not h or now - h[-1] >= self.window]
        for key in idle:
            del self._hits[key]
        if len(self._hits) >= self.max_clients:  # still full: drop everything rather than grow
            self._hits.clear()

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def client_key(request: Request) -> str:
    """The caller's IP address.

    Behind a proxy (Render, a tunnel) every request comes from the proxy, so
    with TRUST_PROXY_HEADERS on, the address the proxy appended last to
    X-Forwarded-For is used. Earlier entries can be forged by the caller and
    are ignored.
    """
    if config.settings.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for", "")
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if parts:
            return parts[-1]
    return request.client.host if request.client else "unknown"
