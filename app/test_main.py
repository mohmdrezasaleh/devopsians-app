import os
from unittest.mock import MagicMock, patch

os.environ.update(REDIS_HOST="x", REDIS_PORT="6379", REDIS_DB="0", REDIS_PASSWORD="")

with patch("redis.Redis", return_value=MagicMock()):
    import main

from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_status():
    r = client.get("/status")
    assert r.status_code == 200
    assert "hostname" in r.json()


def test_visit():
    main.database.incr.return_value = 7
    r = client.post("/visit")
    assert r.json() == {"visits": 7}

def test_metrics():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_request" in r.text
