import os
import s3fs

def upload_model_to_s3_bucket(dir_model):
    # Check local model directory exists
    if not os.path.exists(dir_model):
        raise FileNotFoundError(f"The folder {dir_model} does not exist.")
    assert os.path.isdir(dir_model)

    # Environment config
    S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
    onyxia_user_name = os.environ["GIT_USER_NAME"]
    bucket_name = f"oidc-{onyxia_user_name}"
    dir_model_s3 = f"{bucket_name}/SFINCS_INPUT"

    # Init S3FS
    fs = s3fs.S3FileSystem(client_kwargs={"endpoint_url": S3_ENDPOINT_URL})

    # Remove existing folder on S3 (file-by-file to avoid Content-MD5 errors)
    if fs.exists(dir_model_s3):
        print(f"Removing existing folder '{dir_model_s3}' on S3 (if present)...")
        all_files = fs.find(dir_model_s3)
        for f in all_files:
            fs.rm(f)

    # Upload model files
    list_files = sorted([
        x for x in os.listdir(dir_model)
        if os.path.isfile(os.path.join(dir_model, x))
    ])
    print(f"Uploading files from '{dir_model}' to '{dir_model_s3}':")
    for model_file in list_files:
        local_path = os.path.join(dir_model, model_file)
        remote_path = f"{dir_model_s3}/{model_file}"
        print(f" - {model_file}")
        fs.upload(local_path, remote_path)

    print("Upload finished.")
