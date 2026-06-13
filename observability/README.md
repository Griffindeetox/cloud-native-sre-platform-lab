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
