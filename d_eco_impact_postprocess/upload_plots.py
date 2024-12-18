import os
import shutil
import s3fs

def upload_plots_to_s3_bucket(dir_out):
    # directory with model input files
    if not os.path.exists(dir_out):
        raise FileNotFoundError(f"the folder {dir_out} does not exists, supply a different one")
    assert os.path.isdir(dir_out)

    # setup s3 bucket
    S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
    fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': S3_ENDPOINT_URL})
    onxia_user_name = os.environ["GIT_USER_NAME"] #TODO: convenient to have the username in a separate env var
    bucket_name = f"oidc-{onxia_user_name}"

    # remove dir_out_s3 folder if present, to prevent nested dir_out in dir_out
    dir_out_s3 = f'{bucket_name}/{out}' #alternative option is {os.path.basename(dir_out)}
    if fs.exists(dir_out_s3):
        print(f"removing existing folder '{dir_out_s3}' on s3")
        fs.rm(dir_out_s3, recursive=True)
    
    # upload all files in model directory
    list_files = [x for x in os.listdir(dir_out) if os.path.isfile(os.path.join(dir_out,x))]
    list_files.sort()
    print(f"uploading files from '{dir_out}' to '{dir_out_s3}':")
    for model_file in list_files:
        model_file_full = os.path.join(dir_out, model_file)
        print(f" - {model_file}")
        fs.upload(model_file_full, os.path.join(dir_out_s3,model_file))
    print("upload finished.")
