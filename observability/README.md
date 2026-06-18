## Prometheus Metrics Scraping

The FastAPI application exposes Prometheus-compatible metrics at `/metrics`.

Prometheus is installed through `kube-prometheus-stack` in the `monitoring` namespace. The application runs in the `sre-lab` namespace and is discovered by Prometheus using a `ServiceMonitor`.

### Metrics Flow

```
FastAPI /metrics
  -> Kubernetes Service: sre-fastapi-service
  -> ServiceMonitor: sre-fastapi-servicemonitor
  -> Prometheu Metrics Scraping

The FastAPI application exposes Prometheus-compatible metrics at `/metrics`.

Prometheus is installed through `kube-prometheus-stack` in the `monitoring` namespace. The application runs in the `sre-lab` namespace and is discovered by Prometheus using a `ServiceMonitor`.

### Metrics Flow

```
FastAPI /metrics
  -> Kubernetes Service: sre-fastapi-service
  -> ServiceMonitor: sre-fastapi-servicemonitor
  -> Prometheus

Example Metrics

sre_lab_http_requests_total
sre_lab_http_request_duration_seconds_count
sre_lab_http_request_duration_seconds_sum

Verification
Prometheus successfully scraped both FastAPI pods:

instance="10.42.0.49:8000"
instance="10.42.0.51:8000"
job="sre-fastapi-service"
namespace="sre-lab"
service="sre-fastapi-service"


Prometheus renamed the app label endpoint to exported_endpoint because endpoint is already used as a Prometheus target label.


## Grafana Dashboard

A Grafana dashboard was created to visualize FastAPI application metrics scraped by Prometheus.

### Dashboard Panels

- Request Rate by Endpoint
- Request Rate by Pod
- Total Requests by Endpoint
- P95 Latency by Endpoint
- HTTP Responses by Status Code
- Pod Restarts

### Example PromQL Queries

```promql
sum by (exported_endpoint) (
  rate(sre_lab_http_requests_total[5m])
)
sum by (pod) (
  rate(sre_lab_http_requests_total[5m])
)

histogram_quantile(
  0.95,
  sum by (le, exported_endpoint) (
    rate(sre_lab_http_request_duration_seconds_bucket[5m])
  )
)

SRE Lesson

Dashboards help convert raw metrics into operational visibility. In this lab, Grafana shows request rate, latency, HTTP status codes, pod-level traffic, and restart behavior for the FastAPI service.

## Grafana Dashboard

A Grafana dashboard was created to visualize FastAPI application metrics scraped by Prometheus.

The exported dashboard JSON is stored in this repo as:

```
observability/grafana-dashboard.json

Dashboard Panels
Request Rate by Endpoint
Request Rate by Pod
Total Requests by Endpoint
P95 Latency by Endpoint
HTTP Responses by Status Code
Pod Restarts

Example PromQL Queries

sum by (exported_endpoint) (
  rate(sre_lab_http_requests_total[5m])
)

```

sum by (pod) (
  rate(sre_lab_http_requests_total[5m])
)

```

histogram_quantile(
  0.95,
  sum by (le, exported_endpoint) (
    rate(sre_lab_http_request_duration_seconds_bucket[5m])
  )
)

SRE Lesson

Dashboards help convert raw metrics into operational visibility. In this lab, Grafana shows request rate, latency, HTTP status codes, pod-level traffic, and restart behavior for the FastAPI service.


## Prometheus Alerting

Prometheus alert rules are defined in:

```
k8s/prometheus-rules.yaml

Alerts Added
FastAPIHigh404Rate

Triggers when the FastAPI service returns 404 responses above the configured threshold.

Example expression:

sum(rate(sre_lab_http_requests_total{namespace="sre-lab", http_status="404"}[2m])) > 0.05

FastAPIPodRestartDetected

Triggers when the FastAPI container restart count increases within a 5-minute window.

Example expression:

increase(kube_pod_container_status_restarts_total{namespace="sre-lab", container="sre-fastapi-app"}[5m]) > 0

SRE Lesson

Dashboards help engineers observe system behavior, but alerts help notify when action may be needed. Alert rules should be specific enough to catch real issues without creating unnecessary noise.


## OpenTelemetry Collector

OpenTelemetry was added to the FastAPI application to generate vendor-neutral traces.

The application is instrumented using the OpenTelemetry Python SDK and FastAPI instrumentation. Traces are exported from the FastAPI app to an OpenTelemetry Collector running in the `monitoring` namespace.

### Trace Flow

```text
FastAPI request
  -> OpenTelemetry FastAPI instrumentation
  -> OTLP exporter
  -> OpenTelemetry Collector service
  -> Collector debug exporter logs

Kubernetes Resources

The OpenTelemetry Collector manifest is stored at:

observability/otel-collector.yaml

The Collector exposes OTLP endpoints:

4317 = OTLP gRPC
4318 = OTLP HTTP

The FastAPI Deployment sends traces to the Collector using the in-cluster service DNS name:

http://otel-collector.monitoring.svc.cluster.local:4317

Verification Commands

Check the Collector pod:

kubectl get pods -n monitoring | grep otel

Check Collector logs:

kubectl logs deployment/otel-collector -n monitoring --tail=100

Generate test traffic:

for i in {1..10}; do
  curl -s http://127.0.0.1:8080/version > /dev/null
  curl -s http://127.0.0.1:8080/health > /dev/null
done


SRE Lesson

Prometheus metrics help show what is happening, such as request volume, errors, latency, and restarts. OpenTelemetry traces help show how requests move through a service and provide richer context about request execution.

Using an OpenTelemetry Collector keeps telemetry vendor-neutral and allows traces to be routed to different backends later, such as Grafana Tempo.
