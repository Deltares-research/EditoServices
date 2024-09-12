# Delft3d-fm

## Autosubmit

1- Create a new Autosubmit experiment using this project.
```bash
$ # Create a new Autosubmit experiment using this project
$ autosubmit expid \
    --HPC MN5 \
    --description "Delft3D-fm" \
    --minimal_configuration \
    --git_repo https://github.com/Deltares-research/EditoServices.git \
    --git_branch dflowfm-singularity \
    --git_as_conf "delft3d-fm/autosubmit/conf/"

Autosubmit is running with 4.1.9
The new experiment "a000" has been registered.
Generating folder structure...
Experiment folder: /home/kinow/autosubmit/a000
Generating config files...
Experiment a000 created
```

Modify the `minimal.yml` created for your experiment, in this example:
`~/autosubmit/a000/conf/minimal.yml`. Please, add the following to
your file (indentation matters here).

 ```yaml
# These settings are not necessary for your experiment, but are required
# by Autosubmit: https://earth.bsc.es/gitlab/es/autosubmit/-/issues/1091
PLATFORMS:
  MN5:
    TYPE: slurm
    HOST: glogin1.bsc.es
    PROJECT: ehpc69
    # You need a valid BSC user, in this case from bsc, or adjust
    # the project above and maybe the scratch dir below if needed.
    # Write your username replacing <BSC32_USER>.
    USER: <USER-ID>
    QUEUE: gp_debug
    SCRATCH_DIR: /gpfs/scratch
    ADD_PROJECT_TO_HOST: false
    MAX_WALLCLOCK: 48:00
    TEMP_DIR: ''
 ```

Now run `autosubmit create a000`, followed by `autosubmit run a000`.

After some minutes, you should have successfully executed the workflow
locally, that submits a `SIM` to MareNostrum 5 (note that there is
no platform defined, but the `expid` command was called with `--HPC MN5`
to set the default platform).

You can verify the output log of the `SIM` task (copied to your local
environment by Autosubmit after the successful run of `SIM`) with:

 ```bash
$ autosubmit cat-log -f o a000_SIM
Autosubmit is running with 4.1.9
[INFO] JOBID=3779706

 
 schism develop
 git hash 4511e7e
OK!
 ```

This shows the version of Autosubmit used, and the ID of the Slurm job
executed, followed by the output of the Singularity execution.

For a real execution of the model, adjust the parameters of passed to
the Singularity container. Finally, if you are running this on another
platform, adjust the location of the container.

If you would like to confirm the Slurm jobs were executed, you can
also use the `JOBID` above to query for information, e.g.

```bash
$ sacct -j 3779706 -o jobid,submit,start,end,state
JobID                     Submit               Start                 End      State 
------------ ------------------- ------------------- ------------------- ---------- 
3779706      2024-07-10T13:28:15 2024-07-10T13:28:16 2024-07-10T13:28:20  COMPLETED 
3779706.bat+ 2024-07-10T13:28:16 2024-07-10T13:28:16 2024-07-10T13:28:20  COMPLETED 
3779706.ext+ 2024-07-10T13:28:16 2024-07-10T13:28:16 2024-07-10T13:28:20  COMPLETED 

```

You should also have logs copied to the computer where `autosubmit`
was launched from, e.g. `~/autosubmit/a000/tmp/{LOG_a000,ASLOGS}`.

## SLURM

- run using SLURM
```bash
sbatch --qos=gp_ehpc --account=ehpc69 --partition=gpp --nodes=1 --ntasks-per-node=1 \
  ./submit-slurm-job.sh \ 
  -m <path/to/your/model-dir> \ 
```

- Check the status of the job
```bash
squeue -u <username>
```

- Cancel the job
```bash
scancel <jobid>
```

# MPI Errors

- The following error was observed when running the model regardless of the number of nodes used.
- The error was observed when running the model on the MareNostrum 5 supercomputer using the Singularity container.
- The default MPI library used to develop and test the Singularity container is Intel MPI.

```bash
MPIR_pmi_virtualization(): MPI startup(): PMI calls are forwarded to /host/lib64/libpmi2.so
[0] MPI startup(): Intel(R) MPI Library, Version 2021.12  Build 20240213 (id: 4f55822)
[0] MPI startup(): Copyright (C) 2003-2024 Intel Corporation.  All rights reserved.
[0] MPI startup(): library kind: release
[0] MPI startup(): libfabric version: 1.18.1-impi
[0] MPI startup(): libfabric provider: psm3
[1726132598.969476568] gs03r2b72:rank0.dimr: unknown link speed 0x80
[1726132598.976312809] gs03r2b72:rank0.dimr: Failed to modify UD QP to INIT on mlx5_0: Operation not permitted
Abort(1614735) on node 0 (rank 0 in comm 0): Fatal error in PMPI_Init: Unknown error class, error stack:
MPIR_Init_thread(192)........: 
MPID_Init(1645)..............: 
MPIDI_OFI_mpi_init_hook(1653): 
create_vni_context(2253).....: OFI endpoint open failed (ofi_init.c:2253:create_vni_context:Invalid argument)
srun: error: gs03r2b72: task 0: Exited with exit code 1
srun: Terminating StepId=6375265.0
```

- The used mpi in the cluster is impi/2021.13

```bash
---------------------------------------------------------------------------------------------------------------- /apps/GPP/modulefiles/environment -----------------------------------------------------------------------------------------------------------------
   R/4.2.0-gcc               bsc/1.0        (L)      impi/2021.11                  intel-advisor/2024.0.1     java-openjdk/22.0.1 (D)    nvidia-hpc-sdk/23.11-cuda11.8        oneapi/2023.2.0       (L,D)    perl/5.38.2            python/3.12.1 (D)
   R/4.3.0-BiocM-3.18        ear/ear                 impi/2021.12                  intel-advisor/2024.1       julia/1.10.0               nvidia-hpc-sdk/23.11          (D)    oneapi/2024.0.1                python/3.8.18-gcc      transfer/1.0
   R/4.3.0                   impi/2021.4.0           impi/2021.13                  java-jdk/8u131             miniconda/24.1.2           nvidia-hpc-sdk/24.3                  oneapi/2024.1                  python/3.8.18
   R/4.3.2-cairo             impi/2021.6.0           intel-advisor/2021.4          java-openjdk/11.0.2        miniforge/24.3.0-0         nvidia-hpc-sdk/24.5                  oneapi/2024.2                  python/3.9.16-gcc
   R/4.3.2            (D)    impi/2021.8             intel-advisor/2023.0.0        java-openjdk/11.0.18+10    mpich/4.2.2-gcc            oneapi/2021.4                        openmpi/4.1.5-gcc              python/3.9.16
   anaconda/2023.07   (D)    impi/2021.9.0           intel-advisor/2023.1          java-openjdk/17.0.11+9     mvapich/3.0                oneapi/2023.0                        openmpi/4.1.5-gcc12.3          python/3.12.1-debug
   anaconda/2024.02          impi/2021.10.0 (L,D)    intel-advisor/2023.2.0 (D)    java-openjdk/21.0.3+9      nvidia-hpc-sdk/23.9        oneapi/2023.1                        openmpi/4.1.5         (D)      python/3.12.1-gcc
```

- The error is not consistent, so when the job succeeds, the output is in the file: #dflow-fm/test-case/slurm-62775.out
- Successful runs with both 1 and 2 nodes are included in the files.
  - dflow-fm/test-case/one-node-one-task-successful-job-slurm.out
  - dflow-fm/test-case/two-nodes-two-tasks-per-node-successful-job.out

