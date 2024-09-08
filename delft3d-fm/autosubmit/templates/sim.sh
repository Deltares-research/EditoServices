#!/bin/bash

module load singularity

CONTAINER_LOCATION="/gpfs/projects/bsc32/EDITO/containers/schism2.sif"
CONTAINER_ARGS="/SCHISM/GBconfig/bin/pschism_PREC_EVAP_TVD-SB -v"

singularity exec \
  "${CONTAINER_LOCATION}" \
  ${CONTAINER_ARGS}

echo "OK!"
