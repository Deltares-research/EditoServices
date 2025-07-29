#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# OPTIONAL: create and activate a virtual environment
# python3 -m venv sfincs_env
# source sfincs_env/bin/activate

export GDAL_VERSION=3.6.4

# Upgrade pip
pip install --upgrade pip

# Install packages (GDAL comes bundled via other packages like rasterio/pyproj)
pip install \
  hydromt-sfincs==1.0.2 \
  hydromt==0.8.0 \
  rasterio==1.3.7 \
  geopandas==0.14.1 \
  pandas==2.1.3 \
  xarray==2023.11.0 \
  pyproj==3.6.0 \
  numpy==1.26.0 \
  GDAL==3.6.4

# # Download notebook and helper script
# wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/nbs_sfincs/01_Model_setup.ipynb
# wget https://raw.githubusercontent.com/Deltares-research/EditoServices/main/nbs_sfincs/upload_model.py

# Clear notebook output
jupyter nbconvert --clear-output --inplace 01_Model_setup.ipynb
