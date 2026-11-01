import os
import platform

import psutil
import redis
from fastapi import FastAPI
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
database = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    db=int(os.environ["REDIS_DB"]),
    password=os.environ["REDIS_PASSWORD"],
    decode_responses=True,
)

VISITS = Counter("app_page_visits_total", "Total page visits recorded in Redis")

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
    VISITS.inc()
    return {"visits": database.incr("visits")}
