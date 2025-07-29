#!/bin/bash
set -e  # Exit on any error

### === Install Miniforge (user-local) ===
MINIFORGE=Miniforge3-Linux-x86_64.sh
INSTALL_DIR=$HOME/miniforge3

echo "🔧 Installing Miniforge..."
wget https://github.com/conda-forge/miniforge/releases/latest/download/$MINIFORGE -O $MINIFORGE
bash $MINIFORGE -b -p $INSTALL_DIR
rm $MINIFORGE

# Enable conda commands in this shell
source $INSTALL_DIR/etc/profile.d/conda.sh

### === Create and activate environment ===
echo "🧪 Creating conda environment 'sfincs_vegetation'..."
conda create -y -n sfincs_vegetation python=3.10.13
conda activate sfincs_vegetation

# Install mamba
conda install -y -c conda-forge mamba

### === Install exact packages ===
echo "📦 Installing required packages..."
mamba install -y -c conda-forge \
  hydromt_sfincs=1.0.2 \
  hydromt=0.8.0 \
  rasterio=1.3.7 \
  geopandas=0.14.1 \
  pandas=2.1.3 \
  xarray=2023.11.0 \
  proj=9.2.0 \
  pyproj=3.6.0 \
  numpy=1.26.0 \
  gdal=3.6.4 \
  ipykernel jupyter nbformat nbconvert s3fs boto3

### === Register kernel for Jupyter ===
echo "🔗 Registering Jupyter kernel..."
python -m ipykernel install --user --name sfincs_vegetation --display-name "Python (sfincs_vegetation)"

### === Download notebook and helper script ===
echo "📥 Downloading notebook and script..."
wget -N https://raw.githubusercontent.com/Deltares-research/EditoServices/main/nbs_sfincs/01_Model_setup.ipynb
wget -N https://raw.githubusercontent.com/Deltares-research/EditoServices/main/nbs_sfincs/upload_model.py
wget -N https://raw.githubusercontent.com/Deltares-research/EditoServices/main/nbs_sfincs/run_sfincs_process.py

### === Embed kernel metadata ===
echo "⚙️ Embedding kernel metadata into notebook..."
python - <<EOF
import nbformat

nb_path = "01_Model_setup.ipynb"
nb = nbformat.read(open(nb_path), as_version=nbformat.NO_CONVERT)

nb["metadata"]["kernelspec"] = {
    "name": "sfincs_vegetation",
    "display_name": "Python (sfincs_vegetation)",
    "language": "python"
}

nbformat.write(nb, open(nb_path, "w"))
EOF

### === Clear notebook output ===
echo "🧼 Clearing cell outputs..."
jupyter nbconvert --clear-output --inplace 01_Model_setup.ipynb

echo "✅ Setup complete. You can now open 01_Model_setup.ipynb and it will use the 'sfincs_vegetation' kernel by default."

### === Download input ===
# Make folder
mkdir -p input_dir
cd input_dir

# Base path to raw files on GitHub
BASE_URL="https://github.com/Deltares-research/EditoServices/raw/main/nbs_sfincs/input_dir"

# List of files to download
FILES=(
  da_veg.tif
  delta_dtm_gebco_ref_msl.tif
  domain.gpkg
  domain_lines.gpkg
  edito_sfincs_data.yml
  wl_ts.nc
)

# Download each file
for file in "${FILES[@]}"; do
  echo "Downloading $file..."
  wget -nc "$BASE_URL/$file"
done

cd ..