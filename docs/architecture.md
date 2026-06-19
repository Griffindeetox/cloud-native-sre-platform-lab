# Architecture

## Overview

This lab simulates a small cloud-native SRE platform using a FastAPI service deployed on Kubernetes with monitoring, alerting, and tracing.

The goal is to practice how a service moves from local development to containerization, Kubernetes deployment, operational monitoring, and incident response.

## High-Level Flow

```text
Developer
  -> GitHub Repository
  -> GitHub Actions CI
  -> Docker Image
  -> Kubernetes Deployment
  -> Kubernetes Pods
  -> Kubernetes Service
  -> ServiceMonitor
  -> Prometheus
  -> Grafana Dashboard
  -> Prometheus Alert Rules
  -> OpenTelemetry Collector

Application Layer

The application is a small FastAPI service located in:
app/

It exposes the following endpoints:

/          Root endpoint
/health    Liveness health check
/ready     Readiness check
/version   Application version
/metrics   Prometheus metrics endpoint

The /health endpoint is used by the Kubernetes liveness probe, while /ready is used by the readiness probe.

Container Layer

The application is packaged as a Docker image using:
app/Dockerfile

The image is versioned across lab releases to support rollout and rollback practice.

Example image versions:
sre-fastapi-app:0.1.0
sre-fastapi-app:0.2.0
sre-fastapi-app:0.3.0
sre-fastapi-app:0.4.0
sre-fastapi-app:0.5.0


Kubernetes Layer

The application runs in the sre-lab namespace.

Core Kubernetes resources include:

Namespace
Deployment
Service
ServiceMonitor
PrometheusRule

The Deployment runs two replicas of the FastAPI application. This allows the lab to demonstrate basic high availability and Kubernetes self-healing.

The Service provides a stable internal endpoint for the pods.

Health and Readiness

The Deployment uses:
/health -> livenessProbe
/ready  -> readinessProbe

The liveness probe helps Kubernetes decide when to restart a container.

The readiness probe helps Kubernetes decide whether a pod should receive traffic.

This distinction is important because a container can be running but not ready to serve requests.

Observability Layer

The application exposes Prometheus metrics at:

/metrics

Prometheus discovers the app through a ServiceMonitor.

The metrics include:
sre_lab_http_requests_total
sre_lab_http_request_duration_seconds

Grafana visualizes request rate, latency, HTTP status codes, pod-level traffic, and restarts.

Alerting Layer

Prometheus alert rules are defined in:
k8s/prometheus-rules.yaml

The alert rules currently cover:

High 404 rate
FastAPI pod restart detection

This demonstrates how raw metrics can become actionable operational signals.

Tracing Layer

OpenTelemetry is used to generate traces from the FastAPI application.

Trace flow:
FastAPI request
  -> OpenTelemetry FastAPI instrumentation
  -> OTLP exporter
  -> OpenTelemetry Collector
  -> Collector debug logs

The Collector runs in the monitoring namespace and receives telemetry over OTLP.

CI Layer

GitHub Actions validates the project on push and pull request.

The CI workflow checks:

Python dependency installation
FastAPI app import validation
Project structure
Kubernetes YAML syntax
Docker image build

The workflow does not deploy to Kubernetes because the cluster runs locally on Rancher Desktop.

In a production setup, the next step would be to push the image to a registry and deploy through GitOps or a controlled deployment workflow.

Reliability Scenarios Practiced

The lab includes these SRE exercises:

| Scenario                  | What it demonstrates                         |
| ------------------------- | -------------------------------------------- |
| Pod deletion              | Kubernetes self-healing                      |
| Rollout and rollback      | Deployment safety and recovery               |
| ImagePullBackOff          | Image pull and registry troubleshooting      |
| CrashLoopBackOff          | Runtime/startup failure troubleshooting      |
| Service selector mismatch | Service routing and endpoint troubleshooting |



Future Improvements

Possible future enhancements:

Add Grafana Tempo for trace storage and visualization
Add Loki for log aggregation
Add ArgoCD for GitOps deployment
Push Docker images to GitHub Container Registry
Add Terraform for Kubernetes resource management
Add more alert rules for latency and error rate
