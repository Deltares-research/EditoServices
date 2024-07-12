import os
import shutil
import s3fs

def upload_model_to_s3_bucket(dir_model):
    # directory with model input files
    if not os.path.exists(dir_model):
        raise FileNotFoundError(f"the folder {dir_model} does not exists, supply a different one")
    assert os.path.isdir(dir_model)

    # copy model input files to new folder (exclude data folder)
    dir_model_temp = dir_model + '_TEMP'
    if os.path.exists(dir_model_temp):
        shutil.rmtree(dir_model_temp)
    shutil.copytree(dir_model, dir_model_temp)

    # remove data dir from dir_model_temp
    dir_data = os.path.join(dir_model_temp, "data")
    if os.path.exists(dir_data):
        shutil.rmtree(dir_data)

    # setup s3 bucket
    S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
    fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': S3_ENDPOINT_URL})
    onxia_user_name = os.environ["GIT_USER_NAME"] #TODO: convenient to have the username in a separate env var
    bucket_name = f"oidc-{onxia_user_name}"

    # remove dir_model_s3 folder if present, to prevent nested dir_model in dir_model
    dir_model_s3 = f'{bucket_name}/{os.path.basename(dir_model)}'
    print(f"uploading '{dir_model}' to '{dir_model_s3}'")
    if fs.exists(dir_model_s3):
        print(f"overwriting existing '{dir_model_s3}' folder on s3")
        fs.rm(dir_model_s3, recursive=True)

    fs.upload(dir_model_temp, dir_model_s3, recursive=True)

    # removing local temporary model dir
    shutil.rmtree(dir_model_temp)
    print("upload finished")
    