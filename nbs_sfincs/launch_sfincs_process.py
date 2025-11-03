# launch_sfincs_process.py

from IPython.display import display, Javascript, HTML
from urllib.parse import urlencode, quote

CPU_DEFAULTS = {
    "process_url_path": "process-playground/sfincs-run-docker-test",
    "name": "sfincs-run-docker-test",
    "resources": {
        "resources.requests.cpu": "1800m",
        "resources.requests.memory": "5Gi",
        "resources.limits.cpu": "6400m",
        "resources.limits.memory": "28Gi",
    },
}

GPU_DEFAULTS = {
    "process_url_path": "process-playground/sfincs-run-docker-gpu",
    "name": "sfincs-run-docker-gpu",
    # Intentionally no resource params for GPU.
    "resources": {},
}

def _with_chevrons(v: str) -> str:
    return f"«{v}»"

def _encode_with_chevrons(params: dict) -> str:
    """
    URL-encode query params and ensure chevrons are encoded.
    Values that must be wrapped should already include chevrons.
    """
    qs = urlencode(params, doseq=True, safe="")
    return qs.replace("«", quote("«")).replace("»", quote("»"))

def launch_process_in_browser(
    mode: str = "cpu",                      # "cpu" or "gpu"
    version: str = "0.2.3",
    s3_bucket: str = "region-7e02ff37",
    # CPU resource knobs (used only when mode="cpu")
    cpu_request: str = "1800m",
    memory_request: str = "5Gi",
    cpu_limit: str = "6400m",
    memory_limit: str = "28Gi",
    # General
    auto_launch: bool = True,
    # Optional: add/override arbitrary query params (advanced use)
    extra_params: dict | None = None,
):
    """
    Build and launch the EDITO Process Launcher URL for SFINCS (CPU or GPU).

    - mode="cpu": uses sfincs-run-docker-test with CPU resource params.
    - mode="gpu": uses sfincs-run-docker-gpu with no resource params by default.

    Note: GPU count is not supported and therefore not exposed here.
    """

    mode = mode.lower().strip()
    if mode not in {"cpu", "gpu"}:
        raise ValueError('mode must be "cpu" or "gpu"')

    defaults = CPU_DEFAULTS if mode == "cpu" else GPU_DEFAULTS
    base_url = "https://datalab.dive.edito.eu/process-launcher"

    # Common params
    params = {
        "name": defaults["name"],
        "version": version,
        "s3": s3_bucket,
        "autoLaunch": "true" if auto_launch else "false",
    }

    # Resources only for CPU
    resources = dict(defaults.get("resources") or {})
    if mode == "cpu":
        resources.setdefault("resources.requests.cpu", cpu_request)
        resources.setdefault("resources.requests.memory", memory_request)
        resources.setdefault("resources.limits.cpu", cpu_limit)
        resources.setdefault("resources.limits.memory", memory_limit)

    # Wrap resource values with chevrons
    for k, v in list(resources.items()):
        if v:
            params[k] = _with_chevrons(str(v))

    # Allow arbitrary overrides/additions (no GPU count support implied)
    if extra_params:
        for k, v in extra_params.items():
            if isinstance(v, str) and k.startswith("resources."):
                params[k] = _with_chevrons(v)
            else:
                params[k] = v

    raw_url = f"{base_url}/{defaults['process_url_path']}?{_encode_with_chevrons(params)}"

    # UX: message + auto-open + fallback link
    display(HTML(
        "<b>Launching process in a new tab...</b> "
        "If a pop-up was blocked, use the link below."
    ))
    display(Javascript(f"""
        setTimeout(function() {{
            window.open("{raw_url}", "_blank");
        }}, 2000);
    """))
    display(HTML(f'<a href="{raw_url}" target="_blank">🚀 Click here if auto-launch fails</a>'))

    return raw_url
