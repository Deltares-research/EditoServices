#!/bin/bash
set -euo pipefail

# Copy local test-case data to the remote HPC login node.
# Configuration via environment variables:
# - SSH_USER: required, remote username (e.g., deltXXXXXX)
# - SSH_HOST: required, remote host (e.g., glogin1.bsc.es)
# - LOCAL_DIR: optional, local source directory (default: ./test-case)
# - REMOTE_DIR: optional, remote target directory (default: ~/from-edito)
# - SSH_OPTS: optional, extra ssh/scp options (e.g., "-i /root/.ssh/id_ed25519 -p 22")

SSH_USER="${SSH_USER:-}"
SSH_HOST="${SSH_HOST:-}"
LOCAL_DIR="${LOCAL_DIR:-./test-case}"
REMOTE_DIR="${REMOTE_DIR:-${REMOTE_PATH:-~/from-edito}}"
SSH_OPTS="${SSH_OPTS:-}"

if [ -z "${SSH_USER}" ] || [ -z "${SSH_HOST}" ]; then
  echo "Error: SSH_USER and SSH_HOST must be set." >&2
  exit 1
fi

if [ ! -d "${LOCAL_DIR}" ]; then
  echo "Error: LOCAL_DIR '${LOCAL_DIR}' does not exist." >&2
  exit 1
fi

echo "Ensuring remote directory exists: ${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}"
ssh ${SSH_OPTS} "${SSH_USER}@${SSH_HOST}" "mkdir -p '${REMOTE_DIR}'"

echo "Copying '${LOCAL_DIR}/' to '${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}/'..."
scp -r ${SSH_OPTS} "${LOCAL_DIR}/" "${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}/"

echo "Copy completed."
