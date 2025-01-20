# -*- coding: utf-8 -*-

import os
import json

file_ipynb = "modelbuilder_example.ipynb"

with open(file_ipynb) as f:
    ipynb_json = json.load(f)

# set modeltype to "3D"
replace_success = False
for nbcell in ipynb_json["cells"]:
    for iline, nbline in enumerate(nbcell["source"]):
        pat = 'modeltype = "2D"'
        if nbline.startswith(pat):
            nbline_new = nbline.replace("2D", "3D")
            nbcell["source"][iline] = nbline_new
            replace_success = True
if not replace_success:
    raise ValueError(f"pattern {pat} not found in notebook, could not replace")


edito_header = {
   "cell_type": "markdown",
   # "id": "cf77ed64",
   "metadata": {},
   "source": [
    "## Extra cells added for EDITO platform"
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
ipynb_json["cells"].append(docker_header)
ipynb_json["cells"].append(docker_code)
ipynb_json["cells"].append(upload_header)
ipynb_json["cells"].append(upload_code)

with open(file_ipynb.replace(".ipynb","_edito.ipynb"), "w") as f:
    json.dump(ipynb_json, f, indent=2)
