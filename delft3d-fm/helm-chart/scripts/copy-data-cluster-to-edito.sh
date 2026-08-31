#!/bin/bash
set -euo pipefail

# Copy results from the remote HPC login node to the local pod.
# Configuration via environment variables:
# - SSH_USER: required, remote username (e.g., deltXXXXXX)
# - SSH_HOST: required, remote host (e.g., glogin1.bsc.es)
# - REMOTE_DIR: optional, remote source directory (default: ~/dflowfm)
# - LOCAL_DIR: optional, local target directory (default: ./results)
# - SSH_OPTS: optional, extra ssh/scp options (e.g., "-i /root/.ssh/id_ed25519 -p 22")

SSH_USER="${SSH_USER:-}"
SSH_HOST="${SSH_HOST:-}"
REMOTE_DIR="${REMOTE_DIR:-${REMOTE_PATH:-~/dflowfm}}"
LOCAL_DIR="${LOCAL_DIR:-./results}"
SSH_OPTS="${SSH_OPTS:-}"

if [ -z "${SSH_USER}" ] || [ -z "${SSH_HOST}" ]; then
  echo "Error: SSH_USER and SSH_HOST must be set." >&2
  exit 1
fi

mkdir -p "${LOCAL_DIR}"

echo "Copying '${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}/' to '${LOCAL_DIR}/'..."
scp -r ${SSH_OPTS} "${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}/" "${LOCAL_DIR}/"

echo "Copy completed."
