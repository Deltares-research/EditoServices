#!/bin/bash
set -euxo pipefail

trap 'echo "ERROR: init.sh failed at line $LINENO"' ERR

cd /home/onyxia/work

echo "USER=$(whoami)"
echo "HOME=$HOME"
echo "PWD=$(pwd)"

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
echo "🧪 Creating conda environment 'foccus_ospar'..."
conda create -y -n foccus_ospar python=3.12.2
conda activate foccus_ospar

# Install mamba
conda install -y -c conda-forge mamba

### === Install exact packages ===
echo "📦 Installing required packages..."
mamba install -y -c conda-forge \
  cartopy==0.25.0 \
  cmocean==4.0.3 \
  ipython \
  ipywidgets==8.0.0 \
  matplotlib==3.10.9 \
  numpy==2.4.6 \
  pandas==3.0.3 \
  Shapely==2.1.2 \
  xarray==2026.4.0 \
  xugrid==0.15.2 \
  openpyxl \
  ipykernel jupyter nbformat nbconvert s3fs

### === Register kernel for Jupyter ===
echo "🔗 Registering Jupyter kernel..."
python -m ipykernel install --user --name foccus_ospar --display-name "Python (foccus_ospar)"

### === Download notebook and helper script ===
echo "📥 Downloading notebook and script..."
wget -N https://raw.githubusercontent.com/Deltares-research/EditoServices/main/FOCCUS_OSPAR_demonstrator/main.ipynb
wget -N https://raw.githubusercontent.com/Deltares-research/EditoServices/main/FOCCUS_OSPAR_demonstrator/download_from_s3.py

### === Embed kernel metadata ===
echo "⚙️ Embedding kernel metadata into notebook..."
python - <<EOF
import nbformat

nb_path = "main.ipynb"
nb = nbformat.read(open(nb_path), as_version=nbformat.NO_CONVERT)

nb["metadata"]["kernelspec"] = {
    "name": "foccus_ospar",
    "display_name": "Python (foccus_ospar)",
    "language": "python"
}

nbformat.write(nb, open(nb_path, "w"))
EOF

### === Clear notebook output ===
echo "🧼 Clearing cell outputs..."
jupyter nbconvert --clear-output --inplace main.ipynb

echo "✅ Setup complete. You can now open main.ipynb and it will use the 'foccus_ospar' kernel by default."

### === Download input ===
# Make folder
mkdir -p data
cd data

# Base path to raw files on GitHub
BASE_URL="https://github.com/Deltares-research/EditoServices/raw/main/FOCCUS_OSPAR_demonstrator/data"

# List of files to download
FILES=(
  COMP4_assessment_areas_v8a.cpg
  COMP4_assessment_areas_v8a.dbf
  COMP4_assessment_areas_v8a.sbn
  COMP4_assessment_areas_v8a.sbx
  COMP4_assessment_areas_v8a.shp
  COMP4_assessment_areas_v8a.shx
  OSPAR_metrics_EQR_2015_2020.nc
  River_perTarea_Feb.xlsx
)

# Download each file
for file in "${FILES[@]}"; do
  echo "Downloading $file..."
  wget -nc "$BASE_URL/$file"
done

cd ..

# Make folder
mkdir -p imgs
cd imgs

# Base path to raw files on GitHub
BASE_URL="https://github.com/Deltares-research/EditoServices/raw/main/FOCCUS_OSPAR_demonstrator/imgs"

# List of files to download
FILES=(
  DF111.pdf
  FOCCUS_LOGO.jpg
)

# Download each file
for file in "${FILES[@]}"; do
  echo "Downloading $file..."
  wget -nc "$BASE_URL/$file"
done

cd ..