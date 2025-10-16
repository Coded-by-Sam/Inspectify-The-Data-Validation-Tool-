from flask import Blueprint, send_file, render_template_string
import os
from dotenv import load_dotenv
from validator import validate_dataset_with_expectations

validate_bp = Blueprint('validate_bp', __name__)
load_dotenv()

@validate_bp.route('/validate/<filename>')
def validate_file(filename):
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    report_folder = os.getenv('REPORT_FOLDER', 'reports')

    filepath = os.path.join(upload_folder, filename)

    # Check if file exists
    if not os.path.exists(filepath):
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - File Not Found</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .error-container {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                }
                h1 { color: #e74c3c; margin-bottom: 20px; }
                p { color: #555; line-height: 1.6; }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 25px;
                    transition: all 0.3s;
                }
                a:hover { background: #764ba2; transform: translateY(-2px); }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>❌ File Not Found</h1>
                <p>The file <strong>{{filename}}</strong> could not be found.</p>
                <p>Please upload the file again.</p>
                <a href="/">← Back to Home</a>
            </div>
        </body>
        </html>
        """
        return render_template_string(error_html, filename=filename), 404

    try:
        result = validate_dataset_with_expectations(filepath, report_folder)
        return send_file(result["report_path"], mimetype='text/html')
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Validation Error</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px;
                    margin: 0;
                }}
                .error-container {{
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    max-width: 800px;
                    margin: 0 auto;
                }}
                h1 {{ color: #e74c3c; margin-bottom: 20px; }}
                pre {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    overflow-x: auto;
                    border-left: 4px solid #e74c3c;
                }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 25px;
                    transition: all 0.3s;
                }}
                a:hover {{ background: #764ba2; transform: translateY(-2px); }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>⚠️ Validation Error</h1>
                <p>An error occurred during validation:</p>
                <pre>{str(e)}</pre>
                <a href="/">← Back to Home</a>
            </div>
        </body>
        </html>
        """
        return error_html, 500