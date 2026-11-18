"""Rate limiting on /api/v1/detect."""

import dataclasses
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app import config
from app.main import app, get_detector
from app.rate_limit import RateLimiter


def photo() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64)).save(buffer, format="JPEG")
    return buffer.getvalue()


class NoDetections:
    def detect(self, image):
        return []


@pytest.fixture
def limited(monkeypatch):
    clients = []

    def make(limit: int, trust_proxy: bool = False) -> TestClient:
        monkeypatch.setattr(
            config,
            "settings",
            dataclasses.replace(config.settings, rate_limit_per_minute=limit, trust_proxy_headers=trust_proxy),
        )
        client = TestClient(app)
        client.__enter__()
        clients.append(client)
        app.dependency_overrides[get_detector] = lambda: NoDetections()
        return client

    yield make
    for client in clients:
        client.__exit__(None, None, None)
    # Do not leave a limiter behind for tests that never start the app.
    if hasattr(app.state, "rate_limiter"):
        del app.state.rate_limiter
    app.dependency_overrides.clear()


def scan(client, headers=None):
    return client.post("/api/v1/detect", files={"file": ("p.jpg", photo(), "image/jpeg")}, headers=headers or {})


def test_requests_over_the_limit_get_429_with_retry_after(limited):
    client = limited(2)
    assert scan(client).status_code == 200
    assert scan(client).status_code == 200
    blocked = scan(client)
    assert blocked.status_code == 429
    body = blocked.json()
    assert body["success"] is False and body["error"]["code"] == "RATE_LIMITED"
    assert int(blocked.headers["Retry-After"]) >= 1
    assert blocked.headers["X-Request-ID"] == body["request_id"]


def test_zero_turns_the_limit_off(limited):
    client = limited(0)
    assert all(scan(client).status_code == 200 for _ in range(5))


def test_other_endpoints_are_not_limited(limited):
    client = limited(1)
    scan(client)
    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/categories").status_code == 200


def test_proxy_header_ignored_unless_trusted(limited):
    client = limited(1)
    assert scan(client, {"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    # Without trust, a forged header does not give a fresh allowance.
    assert scan(client, {"X-Forwarded-For": "2.2.2.2"}).status_code == 429


def test_trusted_proxy_uses_last_forwarded_address(limited):
    client = limited(1, trust_proxy=True)
    assert scan(client, {"X-Forwarded-For": "9.9.9.9, 1.1.1.1"}).status_code == 200
    # Same real client (last entry); changing the forgeable first entry does not help.
    assert scan(client, {"X-Forwarded-For": "8.8.8.8, 1.1.1.1"}).status_code == 429
    assert scan(client, {"X-Forwarded-For": "2.2.2.2"}).status_code == 200


def test_window_slides():
    limiter = RateLimiter(2, window=60)
    assert limiter.check("a", now=0) is None
    assert limiter.check("a", now=1) is None
    assert limiter.check("a", now=2) == pytest.approx(58)
    assert limiter.check("a", now=60) is None  # first hit expired
    assert limiter.check("b", now=2) is None  # clients are separate


def test_client_table_does_not_grow_without_bound():
    limiter = RateLimiter(1, window=60, max_clients=3)
    for i, t in enumerate([0, 1, 2]):
        limiter.check(f"c{i}", now=t)
    limiter.check("new", now=100)  # others idle: forgotten
    assert len(limiter._hits) == 1
