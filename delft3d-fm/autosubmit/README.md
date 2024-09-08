# auto-schism2

This project was created as a demo, for the `schism2.sif` singularity
container provided by Hereon / Benjamin. It was successfully tested
on MareNostrum 5 using a personal laptop with Autosubmit, and also
using EDITO Model Lab.

## Instructions

```bash
$ # Create a new Autosubmit experiment using this project
$ autosubmit expid \
    --HPC MN5 \
    --description "Delft3D-fm" \
    --minimal_configuration \
    --git_repo https://github.com/Deltares-research/EditoServices.git \
    --git_branch main \
    --git_as_conf "conf/"
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
EXPERIMENT:
  DATELIST: "20000101"
  MEMBERS: "fc0"
  CHUNKSIZEUNIT: month
  CHUNKSIZE: "4"
  NUMCHUNKS: "2"
  CHUNKINI: ''
  CALENDAR: standard

PLATFORMS:
  MN5:
    TYPE: slurm
    HOST: glogin1.bsc.es
    PROJECT: bsc32
    # You need a valid BSC user, in this case from bsc, or adjust
    # the project above and maybe the scratch dir below if needed.
    # Write your username replacing <BSC32_USER>.
    USER: <BSC32_USER>
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


