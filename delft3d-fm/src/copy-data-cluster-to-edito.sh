#! /bin/bash
echo "Current working directory: ${PWD}"
USER=delt550999
cd "/home/delt/$USER/from-edito"
scp -r $USER@glogin1.bsc.es:dflowfm/ results/
