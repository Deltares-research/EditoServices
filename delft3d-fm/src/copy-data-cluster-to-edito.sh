#! /bin/bash
echo "Current working directory: ${PWD}"
USER=delt550999
scp -r $USER@glogin1.bsc.es:from-edito/dflowfm/ results/
