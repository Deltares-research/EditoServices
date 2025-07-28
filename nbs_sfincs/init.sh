#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Load conda/miniforge environment
module load miniforge

# Initialize conda shell functionality
conda init

# Create and activate the environment
conda create -y --name sfincs_vegetation
source activate sfincs_vegetation

# Install mamba for faster dependency resolution
conda install -y -c conda-forge mamba

# Install required Python packages
mamba install -y -c conda-forge \
  python=3.10.13 \
  hydromt_sfincs=1.0.2 \
  hydromt=0.8.0 \
  rasterio=1.3.7 \
  geopandas=0.14.1 \
  pandas=2.1.3 \
  xarray=2023.11.0 \
  proj=9.2.0 \
  pyproj=3.6.0 \
  numpy=1.26.0 \
  gdal=3.6.4

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

