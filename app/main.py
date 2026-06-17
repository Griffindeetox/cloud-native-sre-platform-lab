from fastapi import FastAPI, Request, Response
from datetime import datetime, timezone
import os
import time

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


APP_VERSION = os.getenv("APP_VERSION", "0.4.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "sre-fastapi-app")


resource = Resource.create(
    {
        "service.name": SERVICE_NAME,
        "service.version": APP_VERSION,
        "deployment.environment": ENVIRONMENT,
    }
)

trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer(__name__)


app = FastAPI(
    title="Cloud-Native SRE Platform Lab",
    description="A small FastAPI service for practicing containers, Kubernetes, CI/CD, and observability.",
    version=APP_VERSION,
)

FastAPIInstrumentor.instrument_app(app)


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
    with tracer.start_as_current_span("root-handler"):
        return {
            "message": "Cloud-Native SRE Platform Lab v0.4.0 is running",
            "environment": ENVIRONMENT,
            "version": APP_VERSION,
        }


@app.get("/health")
def health_check():
    with tracer.start_as_current_span("health-check-handler"):
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/ready")
def readiness_check():
    with tracer.start_as_current_span("readiness-check-handler"):
        return {
            "status": "ready",
            "environment": ENVIRONMENT,
        }


@app.get("/version")
def version():
    with tracer.start_as_current_span("version-handler"):
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
