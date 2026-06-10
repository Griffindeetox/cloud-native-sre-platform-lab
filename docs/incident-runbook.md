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


## Scenario: CrashLoopBackOff

### Goal
Simulate a container runtime failure where the image is valid, but the application process crashes after startup.

### Symptoms
- Pod status shows `CrashLoopBackOff`.
- Container restart count keeps increasing.
- New pod does not become ready.
- Existing healthy pods may continue serving traffic during the failed rollout.

### Commands Used

Check pod status:

```
kubectl get pods -n sre-lab

Describe the failing pod:

```
kubectl describe pod <pod-name> -n sre-lab

Check current container logs:

```
kubectl logs <pod-name> -n sre-lab

Check logs from the previous failed container instance:

```
kubectl logs <pod-name> -n sre-lab --previous

Check namespace events:

```
kubectl get events -n sre-lab --sort-by=.metadata.creationTimestamp

Test service response:

```
curl http://127.0.0.1:8080/version

What Happened

The Deployment was intentionally modified to override the container startup command:

command: ["python"]
args: ["missing_file.py"]

The image sre-fastapi-app:0.2.0 was available locally, so Kubernetes successfully created and started the container. However, the process failed because /app/missing_file.py did not exist.

Evidence

The container logs showed:

python: can't open file '/app/missing_file.py': [Errno 2] No such file or directory

The pod status showed:

CrashLoopBackOff

The events showed:

Back-off restarting failed container sre-fastapi-app

Resolution

The invalid command and args override was removed from k8s/deployment.yaml, allowing the container to use the original Dockerfile command:

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

SRE Lesson

CrashLoopBackOff means Kubernetes can start the container, but the process inside it exits repeatedly. Unlike ImagePullBackOff, application logs are useful here because the container actually starts. kubectl logs --previous is especially important when the container restarts quickly.


## Scenario: Service selector mismatch

### Goal
Simulate a Kubernetes traffic routing issue where pods are healthy, but the Service cannot route traffic to them.

### Symptoms
- Pods are running and ready.
- Deployment is healthy.
- Service exists.
- Service has no endpoints.
- Requests through the Service fail or return no response.

### Commands Used

Check pods:

```
kubectl get pods -n sre-lab

Check Service:

```
kubectl get svc -n sre-lab

Check endpoints:

```
kubectl get endpoints -n sre-lab

Describe the Service:

```
kubectl describe service sre-fastapi-app -n sre-lab

Check pod labels:

```
kubectl get pods -n sre-lab --show -labels

Test service response:

```
curl http://127.0.0.1:8080/version

### What Happened

The Service selector was intentionally changed from:

selector:
  app: sre-fastapi-app

To:

selector:
  app: wrong-app-label

The pods were still running and healthy, but the Service could not find matching backend pods. As a result, the Service had no endpoints.

Evidence

The Service selector did not match the pod labels:

Service selector: app=wrong-app-label
Pod label:        app=sre-fastapi-app

The endpoints output showed no backend pod IPs for the Service.

Resolution

The Service selector was changed back to:

selector:
  app: sre-fastapi-app

After applying the corrected Service manifest, the endpoints returned and traffic through the Service worked again.

SRE Lesson

Not every outage is caused by unhealthy pods. A Service can be misconfigured even when the Deployment is healthy. For traffic issues, always check Service selectors, pod labels, and endpoints.


