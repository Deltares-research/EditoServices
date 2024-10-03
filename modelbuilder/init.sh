#!/bin/bash

# kill process if anything fails
set -e

# we require dfm_tools>=0.29.0 since it works with new CDS
pip install "dfm_tools>=0.29.0"
pip install git+https://github.com/deltares/dfm_tools
wget https://github.com/Deltares/dfm_tools/raw/main/docs/notebooks/modelbuilder_example.ipynb
#wget https://github.com/Deltares/dfm_tools/raw/main/docs/notebooks/postprocessing_example.ipynb
wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/modelbuilder/upload_model.py

# extend modelbuilder notebook
wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/modelbuilder/extend_modelbuilder_notebook.py
jupyter nbconvert --clear-output --inplace modelbuilder_example.ipynb
python extend_modelbuilder_notebook.py
rm extend_modelbuilder_notebook.py
