import os
import shutil
import s3fs

def upload_model_to_s3_bucket(dir_model):
    # directory with model input files
    if not os.path.exists(dir_model):
        raise FileNotFoundError(f"the folder {dir_model} does not exists, supply a different one")
    assert os.path.isdir(dir_model)

    # setup s3 bucket
    S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
    fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': S3_ENDPOINT_URL})
    onxia_user_name = os.environ["GIT_USER_NAME"] #TODO: convenient to have the username in a separate env var
    bucket_name = f"oidc-{onxia_user_name}"

    # remove dir_model_s3 folder if present, to prevent nested dir_model in dir_model
    dir_model_s3 = f'{bucket_name}/{os.path.basename(dir_model)}'
    if fs.exists(dir_model_s3):
        print(f"removing existing folder '{dir_model_s3}' on s3")
        fs.rm(dir_model_s3, recursive=True)
    
    # upload all files in model directory
    list_files = [x for x in os.listdir(dir_model) if os.path.isfile(os.path.join(dir_model,x))]
    list_files.sort()
    print(f"uploading files from '{dir_model}' to '{dir_model_s3}':")
    for model_file in list_files:
        model_file_full = os.path.join(dir_model, model_file)
        print(f" - {model_file}")
        fs.upload(model_file_full, os.path.join(dir_model_s3,model_file))
    print("upload finished.")
