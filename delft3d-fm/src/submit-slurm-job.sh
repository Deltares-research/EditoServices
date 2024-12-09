#! /bin/bash
# This is a script for submitting single or multi-node simulations to the Slurm cluster at Deltares (H7).
# Note: Apptainer is the replacement for Singularity.

# Usage:
#   - Modify this script where needed (e.g. number of nodes, number of tasks per node, Apptainer version).
#   - Execute this script from the command line of H7 using:
#     sbatch ./submit_singularity_h7.sh
#

#--- Specify Slurm SBATCH directives ------------------------------------------------------------------------
#SBATCH --nodes=2               # Number of nodes.
#SBATCH --ntasks-per-node=2     # The number of tasks to be invoked on each node.
                                # For sequential runs, the number of tasks should be '1'.
                                # Note: SLURM_NTASKS is equal to "--nodes" multiplied by "--ntasks-per-node".
#SBATCH --job-name=test_model   # Specify a name for the job allocation.
#SBATCH --time 00:05:00         # Set a limit on the total run time of the job allocation.
#SBATCH --partition=test        # Request a specific partition for the resource allocation.
                                # See: https://publicwiki.deltares.nl/display/Deltareken/Compute+nodes.
##SBATCH --exclusive            # The job allocation can not share nodes with other running jobs.
                                # In many cases this option can be omitted.
##SBATCH --contiguous           # The allocated nodes must form a contiguous set, i.e. next to each other.
                                # In many cases this option can be omitted.

# to run the job on the CPU
# sbatch --partition=test --nodes=2 --ntasks-per-node=2 ./submit-slurm-job.sh -m <path/to/your/mode> -ex dimr -eo dimr_config.xml
# Setup the model
# Specify the ROOT folder of your model, i.e. the folder that contains ALL of the input files and sub-folders, e.g:
# model_dir/
# ├── dflowfm
# │   ├── model.mdu
# │   └── ...
# └── dimr_config.xml

model_dir=/home/delt/delt550999/test-case
# The name of the DIMR configuration file. The default name is dimr_config.xml. This file must already exist!
executable=dimr
executable_opts=dimr_config.xml

#--- Setup the container ------------------------------------------------------------------------------------
# For use within Deltares, Delft3D FM Apptainer containers are available here: P:\d-hydro\delft3dfm_containers\

# Specify the folder that contains the required version of the Apptainer container
RDIR="/gpfs/projects/ehpc69/containers/delft3d-fm"
CONTAINER_PATH="$RDIR/delft3dfm_2024.03_lnx64_sif1227.sif"
SCRIPT_PATH="$RDIR/trigger-container.sh"
#--- Load modules (for use within Deltares) ------------------------------------------------------------------
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
  sed -i "s/\(<process.*>\)[^<>]*\(<\/process.*\)/\1$PROCESSSTR\2/" $dimr_config_dir/$executable_opts

  # The name of the MDU file is read from the DIMR configuration file.
  # You DO NOT need to modify the line below.
  mdu_file="$(sed -n 's/\r//; s/<inputFile>\(.*\).mdu<\/inputFile>/\1/p' $dimr_config_dir/$executable_opts)".mdu
fi


#--- Partition by calling the dflowfm executable -------------------------------------------------------------
if [ "$SLURM_NTASKS" -gt 1 ]; then
    echo ""
    echo "Partitioning parallel model..."
    cd "$mdu_file_dir"
    echo "Partitioning in folder ${PWD}"
    srun -n 1 -N 1 $SCRIPT_PATH -c $CONTAINER_PATH -m "$model_dir" dflowfm --nodisplay --autostartstop --partition:ndomains="$SLURM_NTASKS":icgsolver=6 "$mdu_file"
else
    #--- No partitioning ---
    echo ""
    echo "Sequential model..."
fi

#--- Simulation by calling the dimr executable ----------------------------------------------------------------
echo ""
echo "Simulation..."
cd $dimr_config_dir

echo "Running $executable in dir ${PWD}, with config file $executable_opts"
srun $SCRIPT_PATH -c "$CONTAINER_PATH" -m "$model_dir" "$executable" "$executable_opts"
echo "Submitted job: $SLURM_JOB_ID Number of partitions: $SLURM_NTASKS"
