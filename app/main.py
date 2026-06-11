from fastapi import FastAPI, Request, Response
from datetime import datetime, timezone
import os
import time

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


app = FastAPI(
    title="Cloud-Native SRE Platform Lab",
    description="A small FastAPI service for practicing containers, Kubernetes, CI/CD, and observability.",
    version="0.3.0",
)

APP_VERSION = os.getenv("APP_VERSION", "0.3.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")


REQUEST_COUNT = Counter(
    "sre_lab_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"],
)

REQUEST_LATENCY = Histogram(
    "sre_lab_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    endpoint = request.url.path

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        http_status=response.status_code,
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=endpoint,
    ).observe(duration)

    return response


@app.get("/")
def root():
    return {
        "message": "Cloud-Native SRE Platform Lab v0.3.0 is running",
        "environment": ENVIRONMENT,
        "version": APP_VERSION,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready")
def readiness_check():
    return {
        "status": "ready",
        "environment": ENVIRONMENT,
    }


@app.get("/version")
def version():
    return {
        "app_version": APP_VERSION,
        "environment": ENVIRONMENT,
    }


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
