#!/bin/bash
export IMAGE_ID="decoimpact-notebook"
export VERSION="latest"
export ARTIFACT_REGISTRY_URL="ghcr.io/deltares"
export TAG="${ARTIFACT_REGISTRY_URL}/${IMAGE_ID}:${VERSION}"

docker build . --file Dockerfile --tag "${TAG}"
docker run -p 5001:5001 ${TAG}
