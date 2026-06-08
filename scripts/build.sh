#!/usr/bin/env bash

set -euo pipefail

IMAGE_NAME="sre-fastapi-app"
IMAGE_TAG="0.2.0"

echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"

docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" ./app

echo "Build completed successfully."
