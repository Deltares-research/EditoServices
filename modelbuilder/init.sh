#!/bin/bash

# kill process if anything fails
set -e

pip install dfm_tools
pip install git+https://github.com/deltares/dfm_tools
wget https://github.com/Deltares/dfm_tools/raw/main/docs/notebooks/modelbuilder_example.ipynb
#wget https://github.com/Deltares/dfm_tools/raw/main/docs/notebooks/postprocessing_example.ipynb
wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/modelbuilder/upload_model.py

# extend modelbuilder notebook
wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/modelbuilder/extend_modelbuilder_notebook.py
python extend_modelbuilder_notebook.py modelbuilder_example.ipynb
rm modelbuilder_example.ipynb
rm extend_modelbuilder_notebook.py

# somehow the files get downloaded twice, so delete *.1 files
rm -f *.1
