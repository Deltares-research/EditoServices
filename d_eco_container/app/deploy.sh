#!/bin/bash
export IMAGE_ID="decoimpact-webapp"
export VERSION="latest"
export ARTIFACT_REGISTRY_URL="ghcr.io/deltares"
export TAG="${ARTIFACT_REGISTRY_URL}/${IMAGE_ID}:${VERSION}"

docker run -p 5001:5001 ${TAG}
