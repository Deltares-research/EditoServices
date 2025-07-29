import os
import subprocess
import requests

def run_sfincs_process():
    # Step 0: Refresh token using local script
    editouser = os.environ["GIT_USER_NAME"]
    password = os.environ.get("GIT_PASSWORD")
    if not password:
        import getpass
        password = getpass.getpass(f"🔐 Enter EDITO password for '{editouser}': ")

    # Run the EDITO token refresh script with username + password
    result = subprocess.run(
        ["bash", "-c", f"EDITO_USERNAME='{editouser}' EDITO_PASSWORD='{password}' source /opt/refreshEditoApiAccessToken.sh && env"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"❌ Failed to refresh token.\n{result.stderr}")

    # Extract EDITO_ACCESS_TOKEN from returned environment
    env_lines = result.stdout.splitlines()
    token_line = next((line for line in env_lines if line.startswith("EDITO_ACCESS_TOKEN=")), None)
    if not token_line:
        raise RuntimeError("❌ EDITO_ACCESS_TOKEN not found in output.")
    token = token_line.split("=", 1)[1]

    print("✅ Successfully retrieved EDITO token!")

    # Step 3: Prepare payload
    payload = {
        "metadata": {},
        "processInputs": {
            "onyxia": {
                "friendlyName": "sfincs-run",
                "share": False
            },
            "resources": {
                "limits": {
                    "cpu": "6400m",
                    "memory": "28Gi"
                },
                "requests": {
                    "cpu": "1800m",
                    "memory": "5Gi"
                }
            },
            "s3": {
                "region": "region-7e02ff37"
            }
        }
    }

    # Step 4: Submit process execution
    process_id = "process-playground-sfincs-run-docker-test-0.2.3"
    execution_url = f"https://api.dive.edito.eu/processes/processes/{process_id}/execution"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    res = requests.post(execution_url, headers=headers, json=payload)
    if res.status_code == 201:
        print("✅ Process submitted successfully.")

        location = res.headers.get("Location")
        if location:
            print("🔗 Job location (from header):", location)
        else:
            print("⚠️ No 'Location' header returned.")
            print("📦 Full headers:", res.headers)

            # Try extracting jobId from body (fallback)
            try:
                job_info = res.json()
                job_id = job_info.get("jobId")
                if job_id:
                    print(f"🔗 Job ID (from body): {job_id}")
                    print(f"🔍 Monitor here: https://api.dive.edito.eu/processes/jobs/{job_id}")
                else:
                    print("⚠️ No jobId found in response body.")
            except Exception as e:
                print("⚠️ Failed to parse JSON response body:", e)

    else:
        print("✅ Process submitted successfully.")
        job_location = res.headers.get("Location")
        print("🔗 Job location:", job_location if job_location else "⚠️ Not provided")

        try:
            result_json = res.json()
            print("📦 Response JSON:", result_json)
            job_id = result_json.get("jobId")
            if job_id:
                print(f"🆔 Job ID: {job_id}")
            else:
                print("⚠️ No jobId found in response body.")
        except Exception as e:
            print("❌ Failed to parse JSON response.")
            print("📦 Raw response:", res.text)

    # Step 5: List user's jobs
    print("\n📋 Listing your jobs...")
    jobs_url = "https://api.dive.edito.eu/processes/jobs"
    jobs_res = requests.get(jobs_url, headers=headers)

    print(jobs_res.status_code)
    print(jobs_res.text)

    if jobs_res.ok:
        jobs_data = jobs_res.json()
        for job in jobs_data.get("jobs", []):
            print(f"🆔 Job ID: {job.get('id')}")
            print(f"🔧 Status: {job.get('status')}")
            print(f"📌 Process: {job.get('processId')}")
            print(f"🕒 Submitted: {job.get('submitted')}")
            print("-" * 40)
    else:
        print(f"❌ Failed to list jobs. Status: {jobs_res.status_code}")
        print(jobs_res.text)

if __name__ == "__main__":
    run_sfincs_process()
