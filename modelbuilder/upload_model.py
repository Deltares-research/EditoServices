import os
#import zipfile
import shutil
import s3fs

# zip model input files
dir_model = "Vietnam_model"
#file_zip = f"{dir_model}.zip"
#with zipfile.ZipFile(file_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
#    for dirname, subdirs, files in os.walk(dir_model):
#        if "/data" in dirname:
#            continue
#        zipf.write(dirname)
#        for filename in files:
#            zipf.write(os.path.join(dirname, filename))

# clean dir_model before upload
dir_data = os.path.join(dir_model, "data")
if os.path.exists(dir_data):
    shutil.rmtree(dir_data)

# temporarily add run_docker.sh (maybe move to fm-run-workflow)
file_docker = os.path.join(dir_model,"run_docker.sh")
with open(file_docker, "w") as f:
    f.write("#!/bin/bash")
    f.write("ulimit -s unlimited")
    f.write("/opt/delft3dfm_latest/lnx64/bin/run_dimr.sh -c 1 --dockerparallel --D3D_HOME /opt/delft3dfm_latest/lnx64")

# setup s3 bucket
S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': S3_ENDPOINT_URL})
onxia_user_name = os.environ["GIT_USER_NAME"] #TODO: convenient to have the username in a separate env var
bucket_name = f"oidc-{onxia_user_name}"

# remove dir_model_s3 folder if present, to prevent nested dir_model in dir_model
dir_model_s3 = f'{bucket_name}/{dir_model}'
if fs.exists(dir_model_s3):
    print(f"overwriting existing '{dir_model}' folder on s3")
    fs.rm(dir_model_s3, recursive=True)

#fs.upload(file_zip, f'{bucket_name}/{file_zip}')
fs.upload(dir_model, f'{bucket_name}/{dir_model}', recursive=True)
