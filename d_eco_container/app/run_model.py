import os
# import s3fs
from pathlib import Path

from decoimpact.business.application import Application
from decoimpact.business.workflow.model_builder import ModelBuilder
from decoimpact.crosscutting.i_logger import ILogger
from decoimpact.crosscutting.logger_factory import LoggerFactory
from decoimpact.data.entities.data_access_layer import DataAccessLayer, IDataAccessLayer


def run_model(yaml_path: str):
    """Run the model using the input yaml file and return the output file path"""
    yaml_file_path = Path(yaml_path)

    # configure logger and data-access layer for d-ecoimpact
    logger: ILogger = LoggerFactory.create_logger()
    da_layer: IDataAccessLayer = DataAccessLayer(logger)
    model_builder = ModelBuilder(da_layer, logger)

    # read the input (nc) and output (nc) path from the yaml input file
    model_data = da_layer.read_input_file(yaml_file_path)
    # nc_file = str(model_data.datasets[0].path.relative_to(os.getcwd()))
    output_file_path = str(model_data.output_path)
    # print("output_file_path", output_file_path)
    # download input netCDF (UGrid) file
    # fs.download(f"{bucket_name}/{nc_file}", nc_file)

    # create and run d-ecoimpact application
    application = Application(logger, da_layer, model_builder)
    application.run(yaml_file_path)

    return output_file_path
    # upload the output file to s3
    # fs.upload(output_file_path, f"{bucket_name}/{output_file_path}")
