import os
import platform

import psutil
import redis
from fastapi import FastAPI
from prometheus_client import REGISTRY
from prometheus_client.core import CounterMetricFamily
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
database = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    db=int(os.environ["REDIS_DB"]),
    password=os.environ["REDIS_PASSWORD"],
    decode_responses=True,
)


class RedisVisitsCollector:
    """Exposes the visit counter stored in Redis as a Prometheus counter."""

    def collect(self):
        try:
            value = int(database.get("visits") or 0)
        except redis.RedisError:
            return
        yield CounterMetricFamily(
            "app_page_visits",
            "Total page visits stored in Redis",
            value=value,
        )


REGISTRY.register(RedisVisitsCollector())

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/status")
async def status():
    return {
        "hostname": platform.node(),
        "cpu_percent": psutil.cpu_percent(),
        "ram_percent": psutil.virtual_memory().percent,
        "version": "v2",
    }


@app.post("/visit")
async def visit():
    return {"visits": database.incr("visits")}

@app.get("/error")
async def error():
    raise RuntimeError("intentional error for alert demo")
