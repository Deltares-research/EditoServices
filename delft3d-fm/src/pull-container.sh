#!/bin/bash

#for login docker login containers.deltares.nl with the following credentials:
echo "$HARBOR_PASS" | docker login containers.deltares.nl -u "$HARBOR_USER" --password-stdin


#apptainer pull docker://containers.deltares.nl/base_linux_containers/8-base
apptainer pull docker://containers.deltares.nl/delft3d/dhydro:release-2025.02
