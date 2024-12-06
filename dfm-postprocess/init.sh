#!/bin/bash

# kill process if anything fails
set -e

# we require dfm_tools>=0.29.0 since it works with new CDS
pip install "dfm_tools>=0.29.0"
# pip install git+https://github.com/deltares/dfm_tools
# wget https://github.com/Deltares/dfm_tools/raw/main/docs/notebooks/modelbuilder_example.ipynb
wget https://github.com/Deltares/dfm_tools/raw/main/docs/notebooks/postprocessing_example.ipynb
# wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/modelbuilder/upload_model.py

# clear output
jupyter nbconvert --clear-output --inplace postprocessing_example.ipynb

# extend modelbuilder notebook, creates modelbuilder_example_edito.ipynb
# wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/modelbuilder/extend_modelbuilder_notebook.py
# python extend_modelbuilder_notebook.py
# remove redundant files
# rm modelbuilder_example.ipynb
# rm extend_modelbuilder_notebook.py
