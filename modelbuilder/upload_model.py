import os
import shutil
import s3fs
import argparse

# argument parser
parser = argparse.ArgumentParser(
                    prog='s3-bucket-upload',
                    description='copies the contents of `dir_model` to the folder `delft3dfm_model` on the users s3-bucket')
parser.add_argument('dir_model') # positional argument
args = parser.parse_args()

# directory with model input files
dir_model = args.dir_model
if not os.path.exists(dir_model):
    raise FileNotFoundError(f"the folder {dir_model} does not exists, supply a different one")

# copy model input files to new folder (exclude data folder)
dir_model_temp = dir_model + '_TEMP'
if os.path.exists(dir_model_temp):
    shutil.rmtree(dir_model_temp)
shutil.copytree(dir_model, dir_model_temp)

# remove data dir from dir_model_temp
dir_data = os.path.join(dir_model_temp, "data")
if os.path.exists(dir_data):
    shutil.rmtree(dir_data)

# temporarily add run_docker.sh (maybe move to fm-run-workflow)
file_docker = os.path.join(dir_model_temp,"run_docker.sh")
with open(file_docker, "w") as f:
    f.write("#!/bin/bash\n")
    f.write("ulimit -s unlimited\n")
    f.write("/opt/delft3dfm_latest/lnx64/bin/run_dimr.sh -c 1 --dockerparallel --D3D_HOME /opt/delft3dfm_latest/lnx64\n")

# add run_docker.sh (mdu_file and nproc are derived form dimr_config.xml)
# TODO: this code does not parse nproc from dimr_config.xml properly yet: https://github.com/Deltares/HYDROLIB-core/issues/562
#import dfm_tools as dfmt
#from hydrolib.core.dimr.models import DIMR
#dimr_file = os.path.join(dir_model_temp, "dimr_config.xml")
#dimr_model = DIMR(dimr_file)
#dfmt.modelbuilder.generate_docker_file(dimr_model)

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

fs.upload(dir_model_temp, dir_model_s3, recursive=True)

# removing local temporary model dir
shutil.rmtree(dir_model_temp)
