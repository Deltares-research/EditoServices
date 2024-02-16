import os
from pathlib import Path
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import uuid  # For generating unique IDs for each upload
from run_model import run_model


app = Flask(__name__)
CORS(app)

APP_HOME = os.getenv("APP_HOME")
# Directories for storing uploads
UPLOAD_DIR = f"{APP_HOME}/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Dictionary to track the status of the uploads
upload_status = {}
# Dictionary to track completion of both uploads for an operation
operation_status = {}


def generate_upload_id():
    """Generate a unique ID for each upload"""
    upload_id = uuid.uuid4().hex
    upload_status[input] = 'Pending'
    return upload_id


@app.route("/upload-yaml", methods=["POST"])
def upload_yaml():
    """upload yaml file to the server"""

    # Extract or generate operation_id from request
    operation_id = request.form.get('operation_id', default=uuid.uuid4().hex)
    upload_id = generate_upload_id()
    """upload yaml file to the server"""
    if "yaml_file" not in request.files:
        upload_status[upload_id] = 'Failed: No file part'
        return jsonify({"Error": "Failed: No file part", "upload_id": upload_id}), 400

    file = request.files["yaml_file"]
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        upload_status[upload_id] = 'Failed: No selected file'
        return jsonify({"error": "No selected file", "upload_id": upload_id}), 400

    # Save the file temporarily
    filepath = f"/{APP_HOME}/{file.filename}"
    file.save(filepath)
    upload_status[upload_id] = 'Success'
    # Initialize or update the operation status
    operation_status.setdefault(operation_id, {}).update(
        {'yaml': 'Success', 'yaml_path': filepath}
    )
    check_and_trigger_script(operation_id)
    # Run the script using the uploaded file
    # subprocess.run(["python", "run_model.py", filepath], check=True)
    return jsonify({"message": "YAML file received", "upload_id": upload_id, "operation_id": operation_id}), 200


@app.route('/upload-netcdf', methods=['POST'])
def upload_netcdf():
    """upload netcdf file to the server"""

    # Extract or generate operation_id from request
    operation_id = request.form.get('operation_id', default=uuid.uuid4().hex)
    # Generate a unique ID for this upload
    upload_id = generate_upload_id()
    if 'netcdf_file' not in request.files:
        upload_status[upload_id] = 'Failed: No file part'
        return jsonify({"error": "No file part", "upload_id": upload_id}), 400

    file = request.files['netcdf_file']
    if file.filename == '':
        upload_status[upload_id] = 'Failed: No selected file'
        return jsonify({"error": "No selected file", "upload_id": upload_id}), 400
    # Save the file temporarily, ensure the directory exists
    filepath = f"/{APP_HOME}/{file.filename}"
    file.save(filepath)
    upload_status[upload_id] = 'Success'
    # Initialize or update the operation status
    operation_status.setdefault(operation_id, {}).update(
        {'netcdf': 'Success', 'netcdf_path': filepath, "result_path": None}
    )
    check_and_trigger_script(operation_id)
    return jsonify({"message": "NetCDF file received", "upload_id": upload_id, "operation_id": operation_id}), 200


@app.route('/check-upload/<upload_id>', methods=['GET'])
def check_upload(upload_id):
    # Check the status of the upload by its ID
    status = upload_status.get(upload_id, 'Unknown upload ID')
    return jsonify({"upload_id": upload_id, "status": status})


def check_and_trigger_script(operation_id):
    """Check if both uploads for the operation are successful and trigger the script"""
    operation = operation_status.get(operation_id)
    # Check if both uploads for the operation are successful
    if operation and operation.get('yaml') == 'Success' and operation.get('netcdf') == 'Success':
        yaml_path, netcdf_path = operation['yaml_path'], operation['netcdf_path']
        # print(f"YAML: {yaml_path} and NetCDF: {netcdf_path}")
        # Trigger the script here
        # Assuming both files are successfully uploaded and paths are stored
        if os.path.exists(yaml_path) and os.path.exists(netcdf_path):
            print(f"Triggering script with YAML: {yaml_path} and NetCDF: {netcdf_path}")
            trigger_model(yaml_path, operation_id)
        # Update operation status to indicate script has been run
        operation_status[operation_id]['script_run'] = True
        # print("Script triggered successfully.")
        return jsonify({"message": "Script triggered successfully", "operation_id": operation_id}), 200


def trigger_model(yaml_path, operation_id):
    """Run the model with the uploaded files"""

    try:
        output_file_path = run_model(yaml_path)
        # add the operation_id to the output file path
        # rename the file to have the operation_id
        old_file = Path(output_file_path)
        result_path = f"{old_file.parent}/{old_file.stem}-{operation_id}.nc"
        old_file.rename(result_path)

        # This should be replaced with actual code to generate result.nc
        # result_path = os.path.join(UPLOAD_DIR, new_file.name)
        operation_status[operation_id]['status'] = 'Completed successfully'
        operation_status[operation_id]['result_path'] = result_path

        # Example: Generate result.nc based on yaml_path and netcdf_path
        with open(result_path, "w") as result_file:
            result_file.write("Result of processing YAML and NetCDF")
    except Exception as e:
        operation_status[operation_id]['status'] = 'Failed'


@app.route('/check-run-status/<operation_id>', methods=['GET'])
def check_run_status(operation_id):
    operation = operation_status.get(operation_id)
    if not operation:
        return jsonify({"error": "Invalid operation ID", "operation ID": operation_id}), 404
    status = operation.get('status', 'Processing not started')
    return jsonify({"operation_id": operation_id, "status": status})


@app.route('/get-result/<operation_id>', methods=['GET'])
def get_result(operation_id):
    """Download the result file for the operation"""

    operation = operation_status.get(operation_id)
    print(operation)
    result_filename = operation['result_path']

    if not operation or 'status' not in operation or operation['status'] != 'Completed successfully':
        return jsonify({"error": "Result not available or processing not completed"}), 404
    # Assuming result file is named as "result_<operation_id>.nc"
    if not os.path.exists(result_filename):
        return jsonify({"error": "Result file does not exist"}), 404

    return send_file(result_filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
