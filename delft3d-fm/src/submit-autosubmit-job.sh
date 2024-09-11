#! /bin/bash

model_dir="<path/to/your/model>"
# The name of the DIMR configuration file. The default name is dimr_config.xml. This file must already exist!
executable=dimr
executable_opts=dimr_config.xml

SLURM_NTASKS=1

# Setup the model
# Specify the ROOT folder of your model, i.e. the folder that contains ALL of the input files and sub-folders, e.g:
# model_dir/
# ├── dflowfm
# │   ├── model.mdu
# │   └── ...
# └── dimr_config.xml
# Setup the container
RDIR="/gpfs/projects/ehpc69/containers/delft3d-fm"
CONTAINER_PATH="$RDIR/delft3dfm_2024.03_lnx64_sif1227.sif"
SCRIPT_PATH="$RDIR/trigger-container.sh"


# Load modules
module purge
module load singularity     # Load the Apptainer container system software.
module load impi/2021.12    # Load the  message-passing library for parallel simulations.


# Specify the folder containing your model's MDU file.
mdu_file_dir=$model_dir/dflowfm

# Specify the folder containing your DIMR configuration file.
dimr_config_dir=$model_dir

# This setting might help to prevent errors due to temporary locking of NetCDF files.
export HDF5_USE_FILE_LOCKING=FALSE

# Stop the computation after an error occurs.
set -e

if [ "$executable" = "dimr" ]; then
  # For parallel processes, the lines below update the <process> element in the DIMR configuration file.
  # The updated list of numbered partitions is calculated from the user specified number of nodes and cores.
  # You DO NOT need to modify the lines below.
  PROCESSSTR="$(seq -s " " 0 $((SLURM_NTASKS-1)))"
  sed -i "s/\(<process.*>\)[^<>]*\(<\/process.*\)/\1$PROCESSSTR\2/" "$dimr_config_dir"/"$executable_opts"

  # The name of the MDU file is read from the DIMR configuration file.
  # You DO NOT need to modify the line below.
  mdu_file="$(sed -n 's/\r//; s/<inputFile>\(.*\).mdu<\/inputFile>/\1/p' "$dimr_config_dir"/"$executable_opts")".mdu
fi


#--- Partition by calling the dflowfm executable -------------------------------------------------------------
if [ "$SLURM_NTASKS" -gt 1 ]; then
    echo ""
    echo "Partitioning parallel model..."
    cd "$mdu_file_dir"
    echo "Partitioning in dir ${PWD}"
    "$SCRIPT_PATH" -c "$CONTAINER_PATH" -m "$model_dir" dflowfm --nodisplay --autostartstop --partition:ndomains="$SLURM_NTASKS":icgsolver=6 "$mdu_file"
else
    #--- No partitioning ---
    echo ""
    echo "Sequential model..."
fi

#--- Simulation by calling the dimr executable ----------------------------------------------------------------
echo ""
echo "Simulation..."
cd "$dimr_config_dir"

echo "Running $executable in dir ${PWD}, with config file $executable_opts"
$SCRIPT_PATH -c "$CONTAINER_PATH" -m "$model_dir" "$executable" "$executable_opts"
echo "Submitted job: $SLURM_JOB_ID Number of partitions: $SLURM_NTASKS"
