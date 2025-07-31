import os
import s3fs

def upload_model_to_s3_bucket(dir_model, dir_model_folder_s3, clean_s3=True):
    """
    Uploads all files in a local folder to a target S3 folder.
    
    Parameters:
        dir_model (str): Path to the local folder.
        dir_model_folder_s3 (str): Target folder path inside the user's bucket.
        clean_s3 (bool): If True, removes existing files in the target S3 folder before uploading.
    """
    if not os.path.exists(dir_model):
        raise FileNotFoundError(f"The folder {dir_model} does not exist.")
    assert os.path.isdir(dir_model)

    # Environment config
    S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
    onyxia_user_name = os.environ["GIT_USER_NAME"]
    bucket_name = f"oidc-{onyxia_user_name}"
    dir_model_s3 = f"{bucket_name}/{dir_model_folder_s3}"

    # Init S3FS
    fs = s3fs.S3FileSystem(client_kwargs={"endpoint_url": S3_ENDPOINT_URL})

    # Optional: Clean existing files
    if clean_s3 and fs.exists(dir_model_s3):
        print(f"🧹 Removing existing folder '{dir_model_s3}' on S3...")
        all_files = fs.find(dir_model_s3)
        for f in all_files:
            try:
                fs.rm_file(f)
            except Exception as e:
                print(f"Warning: failed to delete {f}: {e}")

    # Upload files
    list_files = sorted([
        x for x in os.listdir(dir_model)
        if os.path.isfile(os.path.join(dir_model, x))
    ])
    print(f"⬆️ Uploading files from '{dir_model}' to '{dir_model_s3}':")
    for model_file in list_files:
        local_path = os.path.join(dir_model, model_file)
        remote_path = f"{dir_model_s3}/{model_file}"
        print(f" - {model_file}")
        fs.upload(local_path, remote_path)

    print("✅ Upload finished.")
