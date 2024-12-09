#!/bin/bash

# kill process if anything fails
set -e

# we require dfm_tools>=0.29.0 since it works with new CDS
pip install "dfm_tools>=0.29.0"
# pip install git+https://github.com/deltares/dfm_tools

# open notebook
wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/d_eco_impact_postprocess/postprocessing_example.ipynb

# open validation data
#wget wget -p --convert-links -nH -nd -Pvalidation-data https://github.com/Felix-Deltares/EditoServices/raw/0d19ccdb5733f76fcb663c7cc5297135ce2a09e6/d_eco_impact_postprocess/validation-data/zostera_noltei_2017Polygon_WGS84.shp
wget wget -p --convert-links -nH -nd -Pvalidation-data https://github.com/Deltares-research/EditoServices/raw/refs/heads/main/d_eco_impact_postprocess/validation-data/zostera_noltei_2017Polygon_WGS84.cpg
wget wget -p --convert-links -nH -nd -Pvalidation-data https://github.com/Deltares-research/EditoServices/raw/refs/heads/main/d_eco_impact_postprocess/validation-data/zostera_noltei_2017Polygon_WGS84.dbf
wget wget -p --convert-links -nH -nd -Pvalidation-data https://github.com/Deltares-research/EditoServices/raw/refs/heads/main/d_eco_impact_postprocess/validation-data/zostera_noltei_2017Polygon_WGS84.prj
wget wget -p --convert-links -nH -nd -Pvalidation-data https://github.com/Deltares-research/EditoServices/raw/refs/heads/main/d_eco_impact_postprocess/validation-data/zostera_noltei_2017Polygon_WGS84.qmd
wget wget -p --convert-links -nH -nd -Pvalidation-data https://github.com/Deltares-research/EditoServices/raw/refs/heads/main/d_eco_impact_postprocess/validation-data/zostera_noltei_2017Polygon_WGS84.shp
wget wget -p --convert-links -nH -nd -Pvalidation-data https://github.com/Deltares-research/EditoServices/raw/refs/heads/main/d_eco_impact_postprocess/validation-data/zostera_noltei_2017Polygon_WGS84.shx


# clear output
jupyter nbconvert --clear-output --inplace postprocessing_example.ipynb

# extend modelbuilder notebook, creates modelbuilder_example_edito.ipynb
# wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/modelbuilder/extend_modelbuilder_notebook.py
# python extend_modelbuilder_notebook.py
# remove redundant files
# rm modelbuilder_example.ipynb
# rm extend_modelbuilder_notebook.py
