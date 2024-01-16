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

# add run_docker.sh (mdu_file and nproc are derived form dimr_config.xml)
import dfm_tools as dfmt
from hydrolib.core.dimr.models import DIMR
dimr_file = os.path.join(dir_model, "dimr_config.xml")
dimr_model = DIMR(dimr_file)
dfmt.modelbuilder.generate_docker_file(dimr_model)

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
