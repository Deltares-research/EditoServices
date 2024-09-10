#! /bin/bash

# Setup the container
rdir="/gpfs/projects/bsc32/ehpc69/containers/schism2.sif"
container_path=/home/onyxia/work/delft3dfm_2024.03_lnx64_sif1227.sif


# Setup the model
# Specify the ROOT folder of your model, i.e. the folder that contains ALL of the input files and sub-folders, e.g:
# model_dir/
# ├── dflowfm
# │   ├── model.mdu
# │   └── ...
# └── dimr_config.xml

model_dir=/u/farrag/containers/test-case/original
script_path="$model_dir/trigger-container.sh"


# Load modules
module purge
module load apptainer/1.2.5     # Load the Apptainer container system software.
# Load the  message-passing library for parallel simulations.
load impi/2021.10.0
load mkl/2023.2.0
load UCX/1.15.0
load bsc/1.0

# Specify the folder containing your model's MDU file.
mdu_file_dir=$model_dir/dflowfm

# Specify the folder containing your DIMR configuration file.
dimr_config_dir=$model_dir

# The name of the DIMR configuration file. The default name is dimr_config.xml. This file must already exist!
dimr_file=dimr_config.xml

# This setting might help to prevent errors due to temporary locking of NetCDF files.
export HDF5_USE_FILE_LOCKING=FALSE


# Stop the computation after an error occurs.
set -e

# For parallel processes, the lines below update the <process> element in the DIMR configuration file.
# The updated list of numbered partitions is calculated from the user specified number of nodes and cores.
# You DO NOT need to modify the lines below.
PROCESSSTR="$(seq -s " " 0 $((SLURM_NTASKS-1)))"
sed -i "s/\(<process.*>\)[^<>]*\(<\/process.*\)/\1$PROCESSSTR\2/" $dimr_config_dir/$dimr_file

# The name of the MDU file is read from the DIMR configuration file.
# You DO NOT need to modify the line below.
mdu_file="$(sed -n 's/\r//; s/<inputFile>\(.*\).mdu<\/inputFile>/\1/p' $dimr_config_dir/$dimr_file)".mdu


#--- Partition by calling the dflowfm executable -------------------------------------------------------------
if [ "$SLURM_NTASKS" -gt 1 ]; then
    echo ""
    echo "Partitioning parallel model..."
    cd "$mdu_file_dir"
    echo "Partitioning in folder ${PWD}"
    srun -n 1 -N 1 $script_path -c $container_path -m $model_dir dflowfm --nodisplay --autostartstop --partition:ndomains="$SLURM_NTASKS":icgsolver=6 "$mdu_file"
else
    #--- No partitioning ---
    echo ""
    echo "Sequential model..."
fi

#--- Simulation by calling the dimr executable ----------------------------------------------------------------
echo ""
echo "Simulation..."
cd $dimr_config_dir
echo "Computing in folder ${PWD}"
srun $script_path -c $container_path -m $model_dir dimr "$dimr_file"
echo "Submitted job: $SLURM_JOB_ID Number of partitions: $SLURM_NTASKS"
