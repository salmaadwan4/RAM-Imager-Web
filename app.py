from flask import Flask, render_template, request, jsonify
import os
import subprocess
import hashlib
import json
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'captures'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

def load_used_ids():
    if os.path.exists('used_ids.json'):
        with open('used_ids.json', 'r') as f:
            return json.load(f)
    return {"investigator_ids": [], "case_ids": [], "memory_ids": []}

used_ids = load_used_ids()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate_ids():
    data = request.json
    errors = []
    
    if data['investigator_id'] in used_ids['investigator_ids']:
        errors.append("Investigator ID already exists")
    if data['case_id'] in used_ids['case_ids']:
        errors.append("Case ID already exists")
    if data['memory_id'] in used_ids['memory_ids']:
        errors.append("Memory ID already exists")
    
    return jsonify({"errors": errors})

@app.route('/capture', methods=['POST'])
def capture():
    data = request.json
    try:
        if not all([data['investigator_name'], data['case_name'], data['investigator_id']]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(
            app.config['UPLOAD_FOLDER'],
            f"{data['case_name']}_{timestamp}.raw"
        )
        
        result = subprocess.run(
            ["./winpmem_mini.exe", output_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return jsonify({
                "status": "error",
                "message": f"Capture failed: {result.stderr}"
            }), 500
        
        sha256 = hashlib.sha256()
        with open(output_file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        
        used_ids['investigator_ids'].append(data['investigator_id'])
        used_ids['case_ids'].append(data['case_id'])
        used_ids['memory_ids'].append(data['memory_id'])
        with open('used_ids.json', 'w') as f:
            json.dump(used_ids, f)
        
        return jsonify({
            "status": "success",
            "path": output_file,
            "hash": sha256.hexdigest(),
            "size": os.path.getsize(output_file)
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, threaded=True)
