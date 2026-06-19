# Cloud-Native SRE Platform Lab

A hands-on Site Reliability Engineering lab built to practice cloud-native deployment, Kubernetes operations, observability, alerting, and OpenTelemetry using a small FastAPI service.

This project was created to connect traditional SRE skills such as incident response, monitoring, troubleshooting, and reliability thinking with modern cloud-native tooling.

## Project Goal

The goal of this lab is to simulate a small production-style platform where an application is:

* Containerized with Docker
* Deployed to Kubernetes
* Exposed through a Kubernetes Service
* Monitored with Prometheus
* Visualized with Grafana
* Protected with alerting rules
* Instrumented with OpenTelemetry
* Tested through realistic failure scenarios
* Automated with GitHub Actions CI

## Tech Stack

| Area             | Tools                                      |
| ---------------- | ------------------------------------------ |
| Application      | FastAPI, Python                            |
| Containerization | Docker                                     |
| Kubernetes       | Rancher Desktop, k3s, kubectl              |
| CI/CD            | GitHub Actions                             |
| Monitoring       | Prometheus, kube-prometheus-stack          |
| Dashboards       | Grafana                                    |
| Alerting         | PrometheusRule, Alertmanager               |
| Tracing          | OpenTelemetry SDK, OpenTelemetry Collector |
| Documentation    | Markdown runbooks and architecture notes   |

## Architecture Overview

```text
FastAPI App
  -> Docker Image
  -> Kubernetes Deployment
  -> Kubernetes Service
  -> ServiceMonitor
  -> Prometheus
  -> Grafana Dashboard
  -> Prometheus Alert Rules
  -> OpenTelemetry Collector
```

The FastAPI app exposes:

```text
/          - Root endpoint
/health    - Liveness health check
/ready     - Readiness check
/version   - Application version
/metrics   - Prometheus metrics endpoint
```

## Repository Structure

```text
cloud-native-sre-platform-lab/
├── .github/workflows/      # GitHub Actions CI workflow
├── app/                    # FastAPI application and Dockerfile
├── docs/                   # Architecture notes, runbooks, postmortem template
├── k8s/                    # Kubernetes manifests
├── observability/          # Grafana dashboard and OpenTelemetry Collector config
├── scripts/                # Helper scripts
└── README.md
```

## What This Lab Demonstrates

### 1. Application and Containerization

The FastAPI app was first tested locally, then containerized with Docker.

The Docker image is versioned across releases:

```text
sre-fastapi-app:0.1.0
sre-fastapi-app:0.2.0
sre-fastapi-app:0.3.0
sre-fastapi-app:0.4.0
sre-fastapi-app:0.5.0
```

### 2. Kubernetes Deployment

The app runs in a dedicated Kubernetes namespace:

```text
sre-lab
```

Kubernetes resources include:

* Namespace
* Deployment
* Service
* ServiceMonitor
* PrometheusRule

The Deployment uses:

* 2 replicas
* Readiness probe
* Liveness probe
* Resource requests and limits
* Environment variables for version and environment metadata

### 3. Reliability Exercises

This lab includes practical SRE failure simulations:

| Scenario                  | Lesson                                                            |
| ------------------------- | ----------------------------------------------------------------- |
| Pod deletion              | Kubernetes self-healing and desired state reconciliation          |
| Rollout and rollback      | Safe deployment and recovery                                      |
| ImagePullBackOff          | Image name, tag, registry, or authentication issues               |
| CrashLoopBackOff          | Runtime/startup failure inside a valid container                  |
| Service selector mismatch | Healthy pods can still be unreachable if service routing is wrong |

Each scenario is documented in:

```text
docs/incident-runbook.md
```

## Monitoring and Observability

### Prometheus Metrics

The FastAPI app exposes Prometheus-compatible metrics at:

```text
/metrics
```

Custom metrics include:

```promql
sre_lab_http_requests_total
sre_lab_http_request_duration_seconds
```

Prometheus scrapes the app through a Kubernetes `ServiceMonitor`.

### Grafana Dashboard

A Grafana dashboard was created to visualize:

* Request rate by endpoint
* Request rate by pod
* Total requests by endpoint
* P95 latency by endpoint
* HTTP responses by status code
* Pod restarts

The exported dashboard is stored at:

```text
observability/grafana-dashboard.json
```

### Alerting

Prometheus alert rules are defined in:

```text
k8s/prometheus-rules.yaml
```

Alerts include:

* High 404 rate
* FastAPI pod restart detection

### OpenTelemetry

OpenTelemetry was added to generate vendor-neutral traces from the FastAPI service.

Trace flow:

```text
FastAPI request
  -> OpenTelemetry FastAPI instrumentation
  -> OTLP exporter
  -> OpenTelemetry Collector
  -> Collector debug logs
```

The Collector manifest is stored at:

```text
observability/otel-collector.yaml
```

## CI/CD

GitHub Actions is used for basic CI validation.

The workflow checks:

* Python dependency installation
* FastAPI app import validation
* Project structure
* Kubernetes YAML syntax
* Docker image build

Workflow file:

```text
.github/workflows/ci.yml
```

## Useful Commands

Build the Docker image:

```bash
./scripts/build.sh
```

Deploy Kubernetes manifests:

```bash
./scripts/deploy.sh
```

Check app pods:

```bash
kubectl get pods -n sre-lab
```

Check monitoring stack:

```bash
kubectl get pods -n monitoring
```

Port-forward the FastAPI service:

```bash
kubectl port-forward service/sre-fastapi-service 8080:80 -n sre-lab
```

Port-forward Prometheus:

```bash
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring
```

Port-forward Grafana:

```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

Check OpenTelemetry Collector logs:

```bash
kubectl logs deployment/otel-collector -n monitoring --tail=100
```

## SRE Learning Outcomes

This lab helped reinforce:

* How Kubernetes maintains desired state
* How Deployments, ReplicaSets, Pods, and Services work together
* The difference between liveness and readiness
* How to troubleshoot common Kubernetes failure states
* How Prometheus scrapes application metrics
* How Grafana turns metrics into operational dashboards
* How alert rules convert metrics into actionable signals
* How OpenTelemetry provides vendor-neutral tracing
* How CI validates changes before deployment

## Interview Summary

I built this cloud-native SRE lab to connect my existing production SRE and monitoring experience with modern Kubernetes-based reliability practices.

The lab includes a FastAPI service containerized with Docker, deployed to Kubernetes on Rancher Desktop, monitored with Prometheus and Grafana, protected with Prometheus alert rules, and instrumented with OpenTelemetry. I also simulated real failure scenarios such as pod deletion, failed image pulls, crashing containers, rollout/rollback, and service selector mismatch to practice troubleshooting from an SRE perspective.

This project demonstrates practical experience with Kubernetes operations, observability, incident response, deployment safety, and cloud-native reliability engineering.

