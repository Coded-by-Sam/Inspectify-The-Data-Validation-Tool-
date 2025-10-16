import install_reqs
from flask import Flask, render_template
import os
from dotenv import load_dotenv
from upload import upload_bp
from validate import validate_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Load folder paths
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
REPORT_FOLDER = os.getenv('REPORT_FOLDER', 'reports')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(upload_bp)
app.register_blueprint(validate_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)