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

# exec_count_last = max([cell["execution_count"] for cell in ipynb_json["cells"] if cell["cell_type"]=="code"]) +1

dict_1_header = {
   "cell_type": "markdown",
   # "id": "cf77ed64",
   "metadata": {},
   "source": [
    "## Upload to s3 bucket (available on EDITO Datalab only)"
   ]
  }

dict_2_code = {
   "cell_type": "code",
   # "execution_count": 19,
   # "id": "25bcaec2",
   "metadata": {},
   "source": [
    "# upload the generated model to you s3 bucket\n",
    "from upload_model import upload_model_to_s3_bucket\n",
    "upload_model_to_s3_bucket(dir_output)\n"
    "\n"
   ]
  }

ipynb_json["cells"].append(dict_1_header)
ipynb_json["cells"].append(dict_2_code)

with open(file_ipynb.replace(".ipynb","_edito.ipynb"), "w") as f:
    json.dump(ipynb_json, f, indent=2)

