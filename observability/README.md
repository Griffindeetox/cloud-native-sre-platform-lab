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


