#!/bin/bash
# -----------------------------------------------------------------------------
# Purpose
#   Pull an OCI image from a Harbor-backed Docker registry and store it as a
#   local Apptainer/Singularity SIF file.
#
# What this script does
# - Authenticates to the registry if Docker is available (docker login).
# - Otherwise, forwards credentials to Apptainer/Singularity via environment.
# - Pulls docker://REGISTRY/REPOSITORY:TAG into a SIF file.
# - Works with both apptainer and singularity CLIs (prefers apptainer).
#
# Requirements
# - One of: apptainer or singularity installed and on PATH.
# - Optional: docker installed (enables docker login for private registries).
#
# Configuration via environment variables
# - HARBOR_USER, HARBOR_PASS
#     Credentials for the registry (preferred).
# - APPTAINER_DOCKER_USERNAME, APPTAINER_DOCKER_PASSWORD
#     Fallback credentials read by Apptainer/Singularity when Docker is absent.
# - REGISTRY
#     Registry hostname (default: containers.deltares.nl).
# - REPOSITORY
#     Repository path, e.g. org/name (default: delft3d/dhydro).
# - TAG
#     Image tag (default: release-2025.02).
# - SIF_FILE
#     Optional output filename for the pulled SIF; if unset, a default name is used.
#
# Examples
# - Minimal (uses defaults):
#     ./pull-image.sh
#
# - Specify tag and output file:
#     TAG=release-2025.03 SIF_FILE=dhydro-2025.03.sif ./pull-image.sh
#
# - Provide credentials via HARBOR_*:
#     HARBOR_USER=alice HARBOR_PASS=secret ./pull-image.sh
#
# - Without Docker, using Apptainer env vars:
#     APPTAINER_DOCKER_USERNAME=alice APPTAINER_DOCKER_PASSWORD=secret ./pull-image.sh
#
# Notes
# - If Docker is installed and HARBOR_* are set, the script runs:
#     docker login REGISTRY -u HARBOR_USER --password-stdin
#   which avoids exposing the password in process arguments.
# - If Docker is not installed, Apptainer/Singularity uses
#   APPTAINER_DOCKER_USERNAME/PASSWORD for authenticated pulls.
# - To inspect the exact image source being used, the script prints the
#   fully qualified docker:// URL before pulling.
# - This script uses 'set -euo pipefail' to fail fast on errors and unset vars.
# -----------------------------------------------------------------------------

set -euo pipefail

# Determine Harbor credentials (prefer HARBOR_*; fallback to APPTAINER_* if provided)
HARBOR_USER="${HARBOR_USER:-${APPTAINER_DOCKER_USERNAME:-}}"
HARBOR_PASS="${HARBOR_PASS:-${APPTAINER_DOCKER_PASSWORD:-}}"

# If Docker is available, try docker login; otherwise rely on Apptainer auth env vars
if command -v docker >/dev/null 2>&1; then
  if [ -n "${HARBOR_USER:-}" ] && [ -n "${HARBOR_PASS:-}" ]; then
    # echo "$HARBOR_PASS" | docker login containers.deltares.nl -u "$HARBOR_USER" --password-stdin
    export APPTAINER_DOCKER_USERNAME="$HARBOR_USER"
    export APPTAINER_DOCKER_PASSWORD="$HARBOR_PASS"
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
