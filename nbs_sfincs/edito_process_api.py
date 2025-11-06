"""
edito_process_api.py — tiny helper for EDITO Process API from a Jupyter notebook.

Usage example (in a separate cell):

from edito_process_api import EditoClient, build_s3_from_env

client = EditoClient()  # uses EDITO_ACCESS_TOKEN from env

# 1) Inspect a process
proc = client.get_process("process-playground-sfincs-run-docker-gpu-0.2.3")
print(proc["id"], proc["version"], proc.get("title"))

# 2) Build S3 block from AWS_* env vars (host-only endpoint)
s3 = build_s3_from_env()  # raises if something important is missing

# 3) Submit a job
job_url = client.execute_process(
    process_id="process-playground-sfincs-run-docker-gpu-0.2.3",
    metadata={},  # or {"project": "your-group-project-id"}
    process_inputs={
        "onyxia": {"friendlyName": "sfincs-gpu", "share": False},
        "resources": {
            "requests": {"cpu": "1000m", "memory": "4Gi"},
            "limits":   {"cpu": "4000m", "memory": "16Gi", "nvidia.com/gpu": "1"},
        },
        "s3": s3,
    },
)
print("Job URL:", job_url)

# 4) Poll status until done
final = client.wait_for_job(job_url, poll_seconds=5, timeout_seconds=7200)
print(final.get("status"))

# 5) Fetch results (URLs, messages, etc.)
results = client.get_results(job_url)
print(results)
"""
from __future__ import annotations

import os
import time
import json
import typing as t
from dataclasses import dataclass
from urllib.parse import urljoin

import requests


DEFAULT_BASE_URL = "https://api.dive.edito.eu"

# --- EDITO auth helpers ---
import requests, getpass

_DEF_ISSUER = "https://auth.dive.edito.eu/auth/realms/datalab"
_TOKEN_URL  = f"{_DEF_ISSUER}/protocol/openid-connect/token"
_DEF_CLIENT = "edito"
_ENV_VAR    = "EDITO_ACCESS_TOKEN"

def _clean_token(s: str) -> str:
    """Trim and strip accidental 'export EDITO_ACCESS_TOKEN=...' shells."""
    if not s:
        return ""
    s = s.strip()
    # if user pasted the whole 'export EDITO_ACCESS_TOKEN=...' line:
    if s.startswith("export ") and "=" in s:
        s = s.split("=", 1)[1].strip()
    # if token accidentally contains newlines, keep the last JWT-looking part
    parts = [p.strip() for p in s.splitlines() if "." in p]
    if parts:
        return parts[-1]
    return s

def get_bearer_from_env(env_var: str = _ENV_VAR) -> str:
    """Read token from env, clean common formatting issues."""
    return _clean_token(os.environ.get(env_var, ""))

def set_edito_token(
    username: str | None = None,
    password: str | None = None,
    *,
    client_id: str = _DEF_CLIENT,
    issuer: str = _DEF_ISSUER,
    env_var: str = _ENV_VAR,
    store_env: bool = True,
    timeout: int = 30,
) -> str:
    """
    Fetch EDITO access token (Keycloak password grant), set env var, and return it.
    If username/password are None, prompt securely.
    """
    if not username:
        username = input("EDITO username: ").strip()
    if not password:
        password = getpass.getpass("EDITO password: ").strip()

    token_url = f"{issuer}/protocol/openid-connect/token"
    data = {
        "client_id": client_id,
        "username": username,
        "password": password,
        "grant_type": "password",
        "scope": "openid",
    }
    r = requests.post(token_url, data=data, timeout=timeout)
    r.raise_for_status()
    tok = _clean_token(r.json().get("access_token", ""))
    if not tok:
        raise RuntimeError("No access_token returned by issuer.")
    if store_env:
        os.environ[env_var] = tok
    return tok

def _host_only(endpoint: str) -> str:
    """Return host without scheme (strip http:// or https:// if present)."""
    if not endpoint:
        return endpoint
    return endpoint.replace("https://", "").replace("http://", "")


def build_s3_from_env(require_keys: bool = True) -> dict:
    """
    Build an S3 config block from environment variables typically present in Onyxia/EDITO pods.

    Env vars used:
      - AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY
      - AWS_SESSION_TOKEN
      - AWS_S3_ENDPOINT            (host or full URL; we keep host only)
      - AWS_DEFAULT_REGION

    The EDITO init script expects the 'endpoint' *without* scheme (no https://).
    """
    ak = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    sk = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    st = os.getenv("AWS_SESSION_TOKEN", "").strip()
    ep = _host_only(os.getenv("AWS_S3_ENDPOINT", "").strip())
    rg = os.getenv("AWS_DEFAULT_REGION", "").strip()

    missing = []
    if not ep:
        missing.append("AWS_S3_ENDPOINT")
    if not rg:
        missing.append("AWS_DEFAULT_REGION")

    if require_keys:
        if not ak:
            missing.append("AWS_ACCESS_KEY_ID")
        if not sk:
            missing.append("AWS_SECRET_ACCESS_KEY")
        if not st:
            missing.append("AWS_SESSION_TOKEN")

    if missing:
        raise RuntimeError(f"Missing required env vars for S3: {', '.join(missing)}")

    s3 = {
        "enabled": True,
        "endpoint": ep,
        "defaultRegion": rg,
    }
    if ak:
        s3["accessKeyId"] = ak
    if sk:
        s3["secretAccessKey"] = sk
    if st:
        s3["sessionToken"] = st
    return s3


@dataclass
class EditoClient:
    """
    Minimal client for the EDITO Process API.
    Requires an access token in EDITO_ACCESS_TOKEN environment variable by default.
    """
    base_url: str = DEFAULT_BASE_URL
    access_token: t.Optional[str] = None
    timeout: int = 60

    def __post_init__(self):
        # prefer explicit token, else env
        self.access_token = _clean_token(self.access_token) or get_bearer_from_env()
        if not self.access_token:
            raise RuntimeError("Set EDITO_ACCESS_TOKEN in your environment (or call set_edito_token()).")
    
        if not self.base_url.startswith("http"):
            raise ValueError("base_url must start with http/https")

    @classmethod
    def with_credentials(cls, username: str | None = None, password: str | None = None, **kwargs):
        set_edito_token(username, password)  # sets env
        return cls(**kwargs)

    # ---- internal helpers ----
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    def _get(self, path: str) -> dict:
        url = urljoin(self.base_url, path)
        r = requests.get(url, headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: dict) -> requests.Response:
        url = urljoin(self.base_url, path)
        headers = {**self._headers(), "Content-Type": "application/json"}
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=self.timeout)
        r.raise_for_status()
        return r

    # ---- public API ----
    def list_processes(self, limit: int = 100, page: int = 1) -> dict:
        path = f"/processes/processes?limit={limit}&page={page}"
        return self._get(path)

    def get_process(self, process_id: str) -> dict:
        return self._get(f"/processes/processes/{process_id}")

    def execute_process(
        self,
        process_id: str,
        metadata: t.Optional[dict] = None,
        process_inputs: t.Optional[dict] = None,
    ) -> str:
        """Execute a process. Returns the job URL (/processes/jobs/<id>)."""
        payload = {"metadata": metadata or {}, "processInputs": process_inputs or {}}
        resp = self._post(f"/processes/processes/{process_id}/execution", payload)
    
        # Try headers first
        job_url = (resp.headers.get("Location")
                   or resp.headers.get("location")
                   or resp.headers.get("Content-Location")
                   or resp.headers.get("content-location"))
        if job_url:
            return job_url
    
        # Then body variants
        try:
            data = resp.json()
            if "jobID" in data:                      # <— your deployment returns this
                return f"/processes/jobs/{data['jobID']}"
            if "id" in data:
                return f"/processes/jobs/{data['id']}"
            if isinstance(data.get("job"), dict) and "id" in data["job"]:
                return f"/processes/jobs/{data['job']['id']}"
        except Exception:
            pass
    
        # Last resort: list and pick newest for this process (optional: remove if not desired)
        try:
            jobs = self._get("/processes/jobs?limit=200").get("jobs", [])
            cand = [j for j in jobs if (j.get("processId") == process_id) or ((j.get("process") or {}).get("id") == process_id)]
            cand.sort(key=lambda j: j.get("created") or "")
            if cand:
                return f"/processes/jobs/{cand[-1]['id']}"
        except Exception:
            pass
    
        raise RuntimeError("Execution succeeded but no job URL/ID was returned.")

    def get_job(self, job_url_or_id: str) -> dict:
        path = job_url_or_id
        if not path.startswith("/"):
            path = f"/processes/jobs/{path}"
        return self._get(path)

    def get_results(self, job_url_or_id: str) -> dict:
        path = job_url_or_id
        if not path.startswith("/"):
            path = f"/processes/jobs/{path}"
        return self._get(f"{path}/results")

    def wait_for_job(
        self,
        job_url_or_id: str,
        poll_seconds: int = 5,
        timeout_seconds: int = 3600,
        status_fields: t.Sequence[str] = ("status", "state", "phase", "jobStatus", "executionStatus"),
        terminal_states: t.Sequence[str] = ("successful", "failed", "dismissed"),
        echo: bool = True,
    ) -> dict:
        """
        Poll the job until it reaches a terminal state or times out. Returns the final job object.
        """
        start = time.time()
        while True:
            job = self.get_job(job_url_or_id)
            # find first non-empty status-like field
            status = None
            for f in status_fields:
                v = job.get(f)
                if v:
                    status = v
                    break
            if echo:
                ts = time.strftime("%H:%M:%S")
                print(f"{ts}  {status or '(no status)'}")

            if status and str(status).lower() in terminal_states:
                return job

            if time.time() - start > timeout_seconds:
                raise TimeoutError("Timed out waiting for job to finish.")
            time.sleep(poll_seconds)
            
    def wait_until_success(self, job_url_or_id: str, poll_seconds: int = 5, timeout_seconds: int = 7200):
        """
        Wait until the job is 'successful'. Raises if failed/dismissed/timeout.
        Returns the final job JSON.
        """
        job = self.wait_for_job(
            job_url_or_id=job_url_or_id,
            poll_seconds=poll_seconds,
            timeout_seconds=timeout_seconds,
            echo=True,  # keep progress prints
        )
        status = (job.get("status") or job.get("state") or job.get("phase") or "").lower()
        if status != "successful":
            raise RuntimeError(f"Job ended with status '{status}'.")
        return job
    
    # add inside class EditoClient
    def get_results_safe(self, job_url_or_id: str):
        """
        Like get_results(), but returns None if the endpoint is not implemented (404).
        Raises for other HTTP errors.
        """
        try:
            return self.get_results(job_url_or_id)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                return None
            raise

    # add inside class EditoClient
    def submit_and_watch(
        self,
        process_id: str,
        metadata: dict | None,
        process_inputs: dict | None,
        poll_seconds: int = 10,
        timeout_seconds: int = 7200,
        echo: bool = True,
        return_results: bool = True,
    ):
        """
        Execute a process, wait until terminal state, and (optionally) fetch results.
        Returns:
            (job_url, final_job)      if return_results=False
            (job_url, final_job, results_or_none) if return_results=True
        """
        job_url = self.execute_process(process_id, metadata, process_inputs)
        if echo:
            print("Job URL:", job_url)
    
        final_job = self.wait_for_job(
            job_url_or_id=job_url,
            poll_seconds=poll_seconds,
            timeout_seconds=timeout_seconds,
            echo=echo,
        )
    
        if not return_results:
            return job_url, final_job
    
        results = self.get_results_safe(job_url)
        return job_url, final_job, results

