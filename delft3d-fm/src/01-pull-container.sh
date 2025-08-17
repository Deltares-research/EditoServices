#!/bin/bash

set -euo pipefail

# Determine Harbor credentials (prefer HARBOR_*; fallback to APPTAINER_* if provided)
HARBOR_USER="${HARBOR_USER:-${APPTAINER_DOCKER_USERNAME:-}}"
HARBOR_PASS="${HARBOR_PASS:-${APPTAINER_DOCKER_PASSWORD:-}}"

# If Docker is available, try docker login; otherwise rely on Apptainer auth env vars
if command -v docker >/dev/null 2>&1; then
  if [ -n "${HARBOR_USER:-}" ] && [ -n "${HARBOR_PASS:-}" ]; then
    echo "$HARBOR_PASS" | docker login containers.deltares.nl -u "$HARBOR_USER" --password-stdin
  fi
else
  # Export for Apptainer/Singularity to use when pulling from an authenticated Docker registry
  if [ -n "${HARBOR_USER:-}" ]; then export APPTAINER_DOCKER_USERNAME="$HARBOR_USER"; fi
  if [ -n "${HARBOR_PASS:-}" ]; then export APPTAINER_DOCKER_PASSWORD="$HARBOR_PASS"; fi
fi

# Registry parameters (can be overridden via env)
REGISTRY="${REGISTRY:-containers.deltares.nl}"
REPOSITORY="${REPOSITORY:-delft3d/dhydro}"
TAG="${TAG:-release-2025.02}"
SIF_FILE="${SIF_FILE:-}"

# Choose apptainer or singularity executable
APPCMD="apptainer"
if ! command -v "$APPCMD" >/dev/null 2>&1; then
  if command -v singularity >/dev/null 2>&1; then
    APPCMD="singularity"
  fi
fi

echo "Pulling from docker://${REGISTRY}/${REPOSITORY}:${TAG}"
if [ -n "$SIF_FILE" ]; then
  "$APPCMD" pull --name "$SIF_FILE" "docker://${REGISTRY}/${REPOSITORY}:${TAG}"
else
  "$APPCMD" pull "docker://${REGISTRY}/${REPOSITORY}:${TAG}"
fi
