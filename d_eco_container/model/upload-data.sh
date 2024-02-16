#!/bin/bash

# Generate an operation_id (example method, replace with your actual generation logic)
operation_id=$(uuidgen)
URL=http://localhost:5001

echo "operation_id: ${operation_id}"
# Upload YAML file with the operation_id
curl -X POST -F "operation_id=${operation_id}" -F "yaml_file=@input_file.yaml" $URL/upload-yaml

# Upload NetCDF file with the same operation_id
curl -X POST -F "operation_id=${operation_id}" -F "netcdf_file=@FlowFM_net.nc" $URL/upload-netcdf
