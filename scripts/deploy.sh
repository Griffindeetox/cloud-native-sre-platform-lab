#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="sre-lab"

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/

echo "Waiting for deployment rollout..."
kubectl rollout status deployment/sre-fastapi-app -n "${NAMESPACE}"

echo "Deployment completed successfully."
kubectl get pods -n "${NAMESPACE}"
