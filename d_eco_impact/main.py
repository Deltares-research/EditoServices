import os
import s3fs

import decoimpact
from decoimpact.business.application import Application
from decoimpact.business.workflow.model_builder import ModelBuilder
from decoimpact.crosscutting.i_logger import ILogger
from decoimpact.crosscutting.logger_factory import LoggerFactory
from decoimpact.data.entities.data_access_layer import DataAccessLayer, IDataAccessLayer


# Create an file-system object for the s3 bucket
onxia_user_name = os.environ["GIT_USER_NAME"]
bucket_name = f"oidc-{onxia_user_name}"
S3_ENDPOINT_URL = os.environ["S3_ENDPOINT"]
fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': S3_ENDPOINT_URL})

yaml_file = "test.yaml"

# download the yaml file
fs.download(f"{bucket_name}/{yaml_file}", yaml_file)

# configure logger and data-access layer for d-ecoimpact
logger: ILogger = LoggerFactory.create_logger()
da_layer: IDataAccessLayer = DataAccessLayer(logger)
model_builder = ModelBuilder(da_layer, logger)

# read the input (nc) and output (nc) path from the yaml input file
model_data = da_layer.read_input_file(yaml_file)
nc_file = model_data.datasets[0].path
output_file_path = model_data.output_path

# download input netCDF (UGrid) file
fs.download(f"{bucket_name}/{nc_file}", nc_file)

# create and run d-ecoimpact application
application = Application(logger, da_layer, model_builder)
application.run(yaml_file)

# upload the output file to s3
fs.upload(output_file_path, f"{bucket_name}/{output_file_path}")
