import re
import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

# Ensure upload and output directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_gcode_data(gcode_path):
    # Read the gcode file content in binary mode
    with open(gcode_path, 'rb') as file:
        gcode_content = file.read()

    # Decode the content to a string while ignoring errors
    gcode_content = gcode_content.decode(errors='ignore')

    # Define the regular expressions for extracting data
    patterns = {
        "filament_used_mm": r"filament used \[mm\]=([0-9.]+)",
        "filament_used_g": r"filament used \[g\]=([0-9.]+)",
        "filament_cost": r"filament cost=([0-9.]+)",
        "filament_used_cm3": r"filament used \[cm3\]=([0-9.]+)",
        "total_filament_used_wipe_tower_g": r"total filament used for wipe tower \[g\]=([0-9.]+)",
        "estimated_printing_time": r"estimated printing time \(normal mode\)=([0-9m\s0-9s]+)"
    }

    extracted_data = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, gcode_content)
        if match:
            extracted_data[key] = match.group(1)
        else:
            extracted_data[key] = None

    return extracted_data

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.STL'):
        # Save the STL file
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.STL")
        output_path = os.path.join(OUTPUT_FOLDER, f"{file_id}.gcode")
        file.save(input_path)

        # Run PrusaSlicer to generate G-code
        try:
            subprocess.run([
                "prusa-slicer",
                "--load", "config.ini",
                "--output", output_path,
                "--export-gcode",
                input_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"PrusaSlicer failed: {str(e)}"}), 500

        # Extract the data from the generated G-code file
        gcode_data = extract_gcode_data(output_path)

        return jsonify({"data": gcode_data}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
