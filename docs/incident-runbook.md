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

## Scenario: ImagePullBackOff

### Goal
Simulate a failed Kubernetes rollout caused by an invalid container image tag.

### Symptoms
- New pod does not become ready.
- Pod status shows `ErrImagePull` or `ImagePullBackOff`.
- Rollout may hang because Kubernetes cannot start the new pod.
- Existing healthy pods may continue serving traffic.

### Commands Used

Check pod status:

```
kubectl get pods -n sre-lab

Describe the failing pod:

```
kubectl describe pod <pod-name> -n sre-lab

Check namespace events:

```
kubectl get events -n sre-lab --sort-by=.metadata.creationTimestamp

Test current service response:

```
curl http://127.0.0.1:8080/version

Fix the Deployment manifest and apply:

```
kubectl apply -f k8s/deployment.yaml

Confirm rollout recovery:

```
kubectl rollout status deployment/sre-fastapi-app -n sre-lab
kubectl get pods -n sre-lab

What Happened

The Deployment was intentionally updated to use a non-existent image tag: sre-fastapi-app:broken. Kubernetes scheduled a new pod but could not pull the image. The pod first showed ErrImagePull, then moved into ImagePullBackOff as Kubernetes retried and backed off.

Evidence

The pod events showed:

Failed to pull image "sre-fastapi-app:broken": pull access denied for sre-fastapi-app, repository does not exist or may require 'docker login'
Error: ErrImagePull
Error: ImagePullBackOff

Resolution

The image tag in k8s/deployment.yaml was changed back to the valid image:

image: sre-fastapi-app:0.2.0

After applying the corrected manifest, the Deployment recovered and the application continued returning version 0.2.0.

SRE Lesson

ImagePullBackOff usually points to an image name, tag, registry, authentication, or image pull policy problem. Since the container never starts, kubectl describe pod and Kubernetes events are more useful than application logs. A rollout can be failing while old healthy pods continue serving traffic, so rollout status and events must be checked alongside application health.
