#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# OPTIONAL: create and activate a virtual environment
# python3 -m venv sfincs_env
# source sfincs_env/bin/activate

# Install Python packages via pip
pip install --upgrade pip
pip install \
  hydromt-sfincs==1.0.2 \
  hydromt==0.8.0 \
  rasterio==1.3.7 \
  geopandas==0.14.1 \
  pandas==2.1.3 \
  xarray==2023.11.0 \
  proj==9.2.0 \
  pyproj==3.6.0 \
  numpy==1.26.0 \
  GDAL==3.6.4

# Download notebook and helper script
wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/nbs_sfincs/01_Model_setup.ipynb
wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/nbs_sfincs/upload_model.py

# # Download input data
# mkdir -p input-data
# cd input-data
# wget -nc https://github.com/Deltares-research/EditoServices/raw/refs/heads/main/nbs_sfincs/input-data/zostera_noltei_2017Polygon_WGS84.{cpg,dbf,prj,qmd,shp,shx}
# cd ..

# Clear notebook output
jupyter nbconvert --clear-output --inplace 01_Model_setup.ipynb

