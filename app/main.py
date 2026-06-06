
from fastapi import FastAPI
from datetime import datetime, timezone
import os

app = FastAPI(
    title="Cloud-Native SRE Platform Lab",
    description="A small FastAPI service for practicing containers, Kubernetes, CI/CD, and observability.",
    version="0.1.0",
)

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")


@app.get("/")
def root():
    return {
        "message": "Cloud-Native SRE Platform Lab is running",
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
