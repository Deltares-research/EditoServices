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

shutil.rmtree(os.path.join(dir_model, "data"))

# upload zip to s3 bucket
S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': S3_ENDPOINT_URL})
onxia_user_name = os.environ["GIT_USER_NAME"] #TODO: convenient to have the username in a separate env var
bucket_name = f"oidc-{onxia_user_name}"
#fs.upload(file_zip, f'{bucket_name}/{file_zip}')
fs.upload(dir_model, f'{bucket_name}/{dir_model}', recursive=True)
