import os
import s3fs
import boto3

def delete_folder_boto3(bucket_name, prefix, endpoint_url):
    session = boto3.session.Session()
    s3_client = session.client('s3', endpoint_url=endpoint_url)

    # List and delete all objects under the prefix
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' in response:
        delete_keys = [{'Key': obj['Key']} for obj in response['Contents']]
        s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_keys})
        print(f"Deleted {len(delete_keys)} object(s) in '{bucket_name}/{prefix}'")

def upload_model_to_s3_bucket(dir_model):
    # Check directory
    if not os.path.exists(dir_model):
        raise FileNotFoundError(f"The folder '{dir_model}' does not exist.")
    assert os.path.isdir(dir_model)

    # Setup environment and S3
    S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
    onyxia_user_name = os.environ["GIT_USER_NAME"]  # or another env var
    bucket_name = f"oidc-{onyxia_user_name}"
    dir_model_s3 = f"SFINCS_INPUT"  # prefix inside bucket

    fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': S3_ENDPOINT_URL})

    # Delete existing model folder using boto3
    full_prefix = f"{dir_model_s3}/"
    print(f"Removing existing folder '{bucket_name}/{full_prefix}' on s3 (if present)...")
    delete_folder_boto3(bucket_name, full_prefix, S3_ENDPOINT_URL)

    # Upload with s3fs
    list_files = [x for x in os.listdir(dir_model) if os.path.isfile(os.path.join(dir_model, x))]
    list_files.sort()
    print(f"Uploading files from '{dir_model}' to '{bucket_name}/{dir_model_s3}':")
    for model_file in list_files:
        local_path = os.path.join(dir_model, model_file)
        s3_path = f"{bucket_name}/{dir_model_s3}/{model_file}"
        print(f" - {model_file}")
        fs.upload(local_path, s3_path)
    print("Upload finished.")
