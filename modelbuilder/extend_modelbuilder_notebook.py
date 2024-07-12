# -*- coding: utf-8 -*-

import os
import json
import argparse


# argument parser
parser = argparse.ArgumentParser(
                    prog='extend-modelbuider-notebook',
                    description='adds some cells to the modelbuilder notebook')
parser.add_argument('file_ipynb') # positional argument
args = parser.parse_args()

# directory with model input files
file_ipynb = os.path.dirname(args.file_ipynb)
file_ipynb = "modelbuilder_example.ipynb"

with open(file_ipynb) as f:
    ipynb_json = json.load(f)

edito_header = {
   "cell_type": "markdown",
   # "id": "cf77ed64",
   "metadata": {},
   "source": [
    "## Extra cells added for EDITO platform"
   ]
  }

mdu_header = {
   "cell_type": "markdown",
   # "id": "cf77ed64",
   "metadata": {},
   "source": [
    "### Correct an incorrect mdu default"
   ]
  }

mdu_code = {
   "cell_type": "code",
   # "execution_count": 19,
   # "id": "25bcaec2",
   "metadata": {},
   "source": [
    "# replace stretchtype in mdu to support old FM version in docker container until https://github.com/Deltares/HYDROLIB-core/issues/691 is fixed\n",
    "mdu.geometry.stretchtype = 0\n",
    "mdu.save(mdu_file) # ,path_style=path_style)\n",
    "dfmt.make_paths_relative(mdu_file)\n"
   ]
  }

docker_header = {
   "cell_type": "markdown",
   # "id": "cf77ed64",
   "metadata": {},
   "source": [
    "### Rewrite dimr_config.xml and add run_docker.sh (to run on EDITO Datalab)"
   ]
  }

docker_code = {
   "cell_type": "code",
   # "execution_count": 19,
   # "id": "25bcaec2",
   "metadata": {},
   "source": [
    "# rewrite model exec files\n",
    "nproc = 1\n",
    "dimrset_folder = 'docker'\n",
    "dfmt.create_model_exec_files(file_mdu=mdu_file, nproc=nproc, dimrset_folder=dimrset_folder)\n"
   ]
  }

upload_header = {
   "cell_type": "markdown",
   # "id": "cf77ed64",
   "metadata": {},
   "source": [
    "### Upload to s3 bucket (available on EDITO Datalab only)"
   ]
  }

upload_code = {
   "cell_type": "code",
   # "execution_count": 19,
   # "id": "25bcaec2",
   "metadata": {},
   "source": [
    "# upload the generated model to you s3 bucket\n",
    "from upload_model import upload_model_to_s3_bucket\n",
    "upload_model_to_s3_bucket(dir_output)\n"
   ]
  }

ipynb_json["cells"].append(edito_header)
ipynb_json["cells"].append(mdu_header)
ipynb_json["cells"].append(mdu_code)
ipynb_json["cells"].append(docker_header)
ipynb_json["cells"].append(docker_code)
ipynb_json["cells"].append(upload_header)
ipynb_json["cells"].append(upload_code)

with open(file_ipynb.replace(".ipynb","_edito.ipynb"), "w") as f:
    json.dump(ipynb_json, f, indent=2)

