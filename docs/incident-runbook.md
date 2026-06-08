# Incident Runbook

## Scenario: Pod deleted or unexpectedly terminated

### Symptoms
- One pod is missing or terminating.
- Deployment may temporarily show fewer available replicas.
- Service should continue working if at least one ready replica remains.

### Commands Used

Check current pods:

```
kubectl get pods -n sre-lab


Watch pod changes:

```
kubectl get pods -n sre-lab -w

Check rollout status:

```
kubectl rollout status deployment/sre-fastapi-app -n sre-lab

Check Kubernetes events:

```
kubectl get events -n sre-lab --sort-by=.metadata.creationTimestamp

Test service health:

```
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready

What Happened

The Deployment was configured with two replicas. After one pod was deleted, Kubernetes detected that the actual state no longer matched the desired state. The ReplicaSet created a replacement pod automatically.

Resolution

No manual pod recreation was required. Kubernetes restored the Deployment to two running replicas.

SRE Lesson

Deployments provide self-healing by continuously reconciling actual cluster state against the desired state. This improves availability and reduces manual recovery work.


## Scenario: Rollout and rollback validation

### Goal
Practice releasing a new application version and rolling back to the previous known-good version.

### Commands Used

Check rollout status:

```
kubectl rollout status deployment/sre-fastapi-app -n sre-lab

Check rollout history:

```
kubectl rollout history deployment/sre-fastapi-app -n sre-lab

Re-apply desired manifest:

```
kubectl apply -f k8s/deployment.yaml

Test application version:

```
curl http://127.0.0.1:8080/version

What Happened

The application was upgraded from version 0.1.0 to 0.2.0. A rollback restored version 0.1.0 successfully. Re-applying the deployment manifest moved the application back to version 0.2.0.

Observation

A temporary curl: (52) Empty reply from server occurred during rollout/rollback testing. Retrying after the rollout completed returned the correct version. This reinforced the need to verify deployment health using both Kubernetes status commands and application-level health checks.

SRE Lesson

Rollouts and rollbacks are core release safety mechanisms. In production, an SRE should verify rollout status, pod readiness, service health, and application-level behavior before considering a deployment successful.
