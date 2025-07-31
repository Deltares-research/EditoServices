# launch_sfincs_process.py

from IPython.display import display, Javascript, HTML
from urllib.parse import quote


def launch_process_in_browser(
    process_url_path="process-playground/sfincs-run-docker-test",
    version="0.2.3",
    s3_bucket="region-7e02ff37",
    cpu_request="1800m",
    memory_request="5Gi",
    cpu_limit="6400m",
    memory_limit="28Gi",
    auto_launch=True
):
    # Compose the raw URL
    raw_url = (
        f"https://datalab.dive.edito.eu/process-launcher/{process_url_path}"
        f"?name=sfincs-run-docker-test"
        f"&version={version}"
        f"&s3={s3_bucket}"
        f"&resources.requests.cpu=«{cpu_request}»"
        f"&resources.requests.memory=«{memory_request}»"
        f"&resources.limits.cpu=«{cpu_limit}»"
        f"&resources.limits.memory=«{memory_limit}»"
        f"&autoLaunch={'true' if auto_launch else 'false'}"
    )

    # Encode the special characters
    safe_url = raw_url.replace("«", quote("«")).replace("»", quote("»"))

    # Display launch prompt
    display(HTML("<b>Launching process in a new tab... You can return here once it's finished. "
                 "Please check if pop-ups are blocked. If blocked, use the link below:</b>"))

    display(Javascript(f"""
        setTimeout(function() {{
            window.open("{safe_url}", "_blank");
        }}, 2000);
    """))

    display(HTML(f'<a href="{safe_url}" target="_blank">🚀 Click here if auto-launch fails</a>'))
