import os
import shutil
from flask import Blueprint, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload_bp', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_folders():
    """Remove all files from uploads and reports folders"""
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    report_folder = os.getenv('REPORT_FOLDER', 'reports')
    
    # Clean uploads folder
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    
    # Clean reports folder
    if os.path.exists(report_folder):
        for filename in os.listdir(report_folder):
            file_path = os.path.join(report_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    # Clean previous uploads before accepting new one
    clean_folders()
    
    if 'dataset' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files['dataset']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "status": "error", 
            "message": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    # Secure the filename
    filename = secure_filename(file.filename)
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, filename)
    
    try:
        file.save(filepath)
        # Return success with redirect URL
        return jsonify({
            "status": "success", 
            "message": "File uploaded successfully",
            "redirect": url_for('validate_bp.validate_file', filename=filename)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error saving file: {str(e)}"}), 500