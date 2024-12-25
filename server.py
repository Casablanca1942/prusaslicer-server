from flask import Flask, request, jsonify, send_file
import os
import subprocess
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

# Ensure upload and output directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.stl'):
        # Save the STL file
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.stl")
        output_path = os.path.join(OUTPUT_FOLDER, f"{file_id}.gcode")
        file.save(input_path)

        # Run PrusaSlicer to generate G-code
        try:
            subprocess.run([
                "prusa-slicer",
                "--load", "config.ini",
                "--output", output_path,
                input_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"PrusaSlicer failed: {str(e)}"}), 500

        return jsonify({"gcode_file": f"/download/{file_id}.gcode"}), 200
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
