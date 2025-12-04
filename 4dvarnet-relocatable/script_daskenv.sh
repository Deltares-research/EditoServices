#!/bin/bash

#SBATCH --job-name=test_4dvarnotebook
#SBATCH --partition=gpu-shared
##SBATCH --ntasks 2
#SBATCH --time=0-04:00:00           
#SBATCH --output=out_tes.log  
#SBATCH --error=error_tes.log 
    
     
module load miniforge/latest
/p/11210528-foccus/05-Models/WP6/4DVarNet/JupyterNotebook/4dvarnet_trial/bin/python SameWorkflow_nowPY_forGPUtests.py