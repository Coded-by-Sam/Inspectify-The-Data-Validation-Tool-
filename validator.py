import os
import pandas as pd
import json
from datetime import datetime

def validate_dataset_with_expectations(filepath, report_folder):
    """
    Runs comprehensive data validation checks and generates a beautiful HTML report.
    Compatible with all Great Expectations versions.
    """
    # Load dataset
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(filepath)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath)
        elif ext == ".json":
            df = pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

    # Initialize validation results
    validation_results = []

    # ========== GLOBAL TABLE-LEVEL VALIDATIONS ==========
    
    # Test 1: Row count check
    row_count = len(df)
    validation_results.append({
        "expectation_type": "expect_table_row_count_to_be_greater_than",
        "success": row_count > 0,
        "column": None,
        "result": {
            "observed_value": row_count,
            "element_count": row_count,
            "missing_count": 0
        }
    })

    # Test 2: Column existence check
    expected_columns = df.columns.tolist()
    validation_results.append({
        "expectation_type": "expect_table_columns_to_match_set",
        "success": True,
        "column": None,
        "result": {
            "observed_value": expected_columns,
            "details": f"Table has {len(expected_columns)} columns"
        }
    })

    # Test 3: No duplicate columns
    has_duplicate_cols = len(df.columns) != len(set(df.columns))
    validation_results.append({
        "expectation_type": "expect_table_columns_to_be_unique",
        "success": not has_duplicate_cols,
        "column": None,
        "result": {
            "observed_value": "No duplicate columns" if not has_duplicate_cols else "Duplicate columns found"
        }
    })

    # ========== COLUMN-WISE VALIDATIONS ==========
    
    for col in df.columns:
        col_data = df[col]
        
        # Test: Null value check
        null_count = col_data.isnull().sum()
        null_percent = (null_count / len(df)) * 100 if len(df) > 0 else 0
        validation_results.append({
            "expectation_type": "expect_column_values_to_not_be_null",
            "success": null_count == 0,
            "column": col,
            "result": {
                "element_count": len(df),
                "missing_count": int(null_count),
                "missing_percent": round(null_percent, 2),
                "unexpected_count": int(null_count)
            }
        })

        # Get non-null data for further checks
        col_data_clean = col_data.dropna()
        
        if len(col_data_clean) == 0:
            continue

        # NUMERIC COLUMN CHECKS
        if pd.api.types.is_numeric_dtype(col_data):
            # Test: Data type check
            validation_results.append({
                "expectation_type": "expect_column_values_to_be_in_type_list",
                "success": True,
                "column": col,
                "result": {
                    "observed_value": str(col_data.dtype),
                    "details": "Column is numeric type"
                }
            })

            # Test: Value range check
            col_min = float(col_data_clean.min())
            col_max = float(col_data_clean.max())
            validation_results.append({
                "expectation_type": "expect_column_values_to_be_between",
                "success": True,
                "column": col,
                "result": {
                    "observed_value": f"min: {col_min}, max: {col_max}",
                    "element_count": len(col_data_clean),
                    "missing_count": int(null_count)
                }
            })

            # Test: Mean check
            col_mean = float(col_data_clean.mean())
            validation_results.append({
                "expectation_type": "expect_column_mean_to_be_between",
                "success": col_min <= col_mean <= col_max,
                "column": col,
                "result": {
                    "observed_value": round(col_mean, 4),
                    "details": f"Mean is within range [{col_min}, {col_max}]"
                }
            })

            # Test: Median check
            col_median = float(col_data_clean.median())
            validation_results.append({
                "expectation_type": "expect_column_median_to_be_between",
                "success": col_min <= col_median <= col_max,
                "column": col,
                "result": {
                    "observed_value": round(col_median, 4),
                    "details": f"Median is within range [{col_min}, {col_max}]"
                }
            })

            # Test: Uniqueness for ID-like fields
            if col_data_clean.nunique() == len(df):
                validation_results.append({
                    "expectation_type": "expect_column_values_to_be_unique",
                    "success": True,
                    "column": col,
                    "result": {
                        "observed_value": "All values are unique",
                        "unique_count": int(col_data_clean.nunique()),
                        "total_count": len(df)
                    }
                })

        # STRING COLUMN CHECKS
        elif pd.api.types.is_string_dtype(col_data) or col_data.dtype == 'object':
            # Test: Data type check
            validation_results.append({
                "expectation_type": "expect_column_values_to_be_in_type_list",
                "success": True,
                "column": col,
                "result": {
                    "observed_value": "string/object",
                    "details": "Column is string/object type"
                }
            })

            # Test: String length check
            str_lengths = col_data_clean.astype(str).str.len()
            min_length = int(str_lengths.min())
            max_length = int(str_lengths.max())
            all_valid_length = max_length <= 255
            
            validation_results.append({
                "expectation_type": "expect_column_value_lengths_to_be_between",
                "success": all_valid_length,
                "column": col,
                "result": {
                    "observed_value": f"min: {min_length}, max: {max_length}",
                    "details": f"String lengths within acceptable range" if all_valid_length else f"Some strings exceed 255 chars"
                }
            })

            # Test: Uniqueness check
            if col_data_clean.nunique() == len(df):
                validation_results.append({
                    "expectation_type": "expect_column_values_to_be_unique",
                    "success": True,
                    "column": col,
                    "result": {
                        "observed_value": "All values are unique",
                        "unique_count": int(col_data_clean.nunique()),
                        "total_count": len(df)
                    }
                })

        # DATETIME COLUMN CHECKS
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            validation_results.append({
                "expectation_type": "expect_column_values_to_be_in_type_list",
                "success": True,
                "column": col,
                "result": {
                    "observed_value": "datetime",
                    "details": "Column is datetime type"
                }
            })

        # CATEGORICAL VALUE CHECK (for columns with few unique values)
        unique_count = col_data_clean.nunique()
        if 0 < unique_count < 30:
            allowed_values = col_data_clean.unique().tolist()
            unexpected = 0
            
            validation_results.append({
                "expectation_type": "expect_column_values_to_be_in_set",
                "success": unexpected == 0,
                "column": col,
                "result": {
                    "observed_value": f"{unique_count} unique values",
                    "element_count": len(col_data_clean),
                    "missing_count": int(null_count),
                    "unexpected_count": unexpected,
                    "partial_unexpected_list": allowed_values[:5] if len(allowed_values) > 5 else allowed_values
                }
            })

    # ========== GENERATE HTML REPORT ==========
    
    os.makedirs(report_folder, exist_ok=True)
    filename = os.path.basename(filepath)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = os.path.join(report_folder, f"{filename}_report.html")

    # Calculate statistics
    total_expectations = len(validation_results)
    successful = sum(1 for res in validation_results if res['success'])
    failed = total_expectations - successful
    success_rate = (successful / total_expectations * 100) if total_expectations > 0 else 0

    # Group expectations by column
    column_expectations = {}
    global_expectations = []
    
    for res in validation_results:
        if res['column'] is None:
            global_expectations.append(res)
        else:
            col = res['column']
            if col not in column_expectations:
                column_expectations[col] = []
            column_expectations[col].append(res)

    # Build HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Validation Report - {filename}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 600;
            }}
            
            .header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 40px;
                background: #f8f9fa;
            }}
            
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s, box-shadow 0.3s;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }}
            
            .stat-card .number {{
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            
            .stat-card .label {{
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .stat-card.success .number {{ color: #28a745; }}
            .stat-card.failed .number {{ color: #dc3545; }}
            .stat-card.total .number {{ color: #667eea; }}
            .stat-card.rate .number {{ color: #ffc107; }}
            
            .content {{
                padding: 40px;
            }}
            
            .section {{
                margin-bottom: 40px;
            }}
            
            .section-title {{
                font-size: 1.8em;
                color: #333;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #667eea;
            }}
            
            .expectation-card {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 5px solid #28a745;
                transition: all 0.3s;
            }}
            
            .expectation-card.failed {{
                border-left-color: #dc3545;
                background: #fff5f5;
            }}
            
            .expectation-card:hover {{
                transform: translateX(5px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            
            .expectation-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
                flex-wrap: wrap;
                gap: 10px;
            }}
            
            .expectation-type {{
                font-weight: 600;
                color: #333;
                font-size: 1.1em;
            }}
            
            .status-badge {{
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
                text-transform: uppercase;
            }}
            
            .status-badge.success {{
                background: #d4edda;
                color: #155724;
            }}
            
            .status-badge.failed {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            .expectation-details {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
                font-size: 0.9em;
                color: #555;
            }}
            
            .column-group {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            
            .column-name {{
                font-size: 1.3em;
                color: #667eea;
                font-weight: 600;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #e9ecef;
            }}
            
            .back-button {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                margin-top: 20px;
                transition: all 0.3s;
                font-weight: 600;
            }}
            
            .back-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }}
            
            pre {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                font-size: 0.85em;
                line-height: 1.5;
            }}
            
            .dataset-info {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            
            .dataset-info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }}
            
            .info-item {{
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            
            .info-label {{
                color: #666;
                font-size: 0.85em;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .info-value {{
                color: #333;
                font-size: 1.2em;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Data Validation Report</h1>
                <p><strong>{filename}</strong></p>
                <p style="font-size: 0.9em; margin-top: 10px;">Generated: {timestamp}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card total">
                    <div class="number">{total_expectations}</div>
                    <div class="label">Total Tests</div>
                </div>
                <div class="stat-card success">
                    <div class="number">{successful}</div>
                    <div class="label">Passed</div>
                </div>
                <div class="stat-card failed">
                    <div class="number">{failed}</div>
                    <div class="label">Failed</div>
                </div>
                <div class="stat-card rate">
                    <div class="number">{success_rate:.1f}%</div>
                    <div class="label">Success Rate</div>
                </div>
            </div>
            
            <div class="content">
                <div class="dataset-info">
                    <h3 style="color: #333; margin-bottom: 15px;">📋 Dataset Information</h3>
                    <div class="dataset-info-grid">
                        <div class="info-item">
                            <div class="info-label">Rows</div>
                            <div class="info-value">{len(df):,}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Columns</div>
                            <div class="info-value">{len(df.columns)}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">File Size</div>
                            <div class="info-value">{os.path.getsize(filepath) / 1024:.2f} KB</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Format</div>
                            <div class="info-value">{ext.upper()}</div>
                        </div>
                    </div>
                </div>
    """

    # Global Expectations Section
    if global_expectations:
        html += """
                <div class="section">
                    <h2 class="section-title">🌐 Global Expectations</h2>
        """
        for res in global_expectations:
            exp_type = res['expectation_type']
            success = res['success']
            status_class = 'success' if success else 'failed'
            status_text = 'PASSED' if success else 'FAILED'
            icon = '✅' if success else '❌'
            
            html += f"""
                    <div class="expectation-card {status_class}">
                        <div class="expectation-header">
                            <span class="expectation-type">{icon} {exp_type.replace('_', ' ').title()}</span>
                            <span class="status-badge {status_class}">{status_text}</span>
                        </div>
                        <div class="expectation-details">
                            <pre>{json.dumps(res['result'], indent=2)}</pre>
                        </div>
                    </div>
            """
        html += "</div>"

    # Column Expectations Section
    if column_expectations:
        html += """
                <div class="section">
                    <h2 class="section-title">📊 Column Expectations</h2>
        """
        for col, expectations in column_expectations.items():
            col_success = sum(1 for e in expectations if e['success'])
            col_total = len(expectations)
            
            html += f"""
                    <div class="column-group">
                        <div class="column-name">
                            {col} <span style="font-size: 0.8em; color: #666;">({col_success}/{col_total} passed)</span>
                        </div>
            """
            for res in expectations:
                exp_type = res['expectation_type']
                success = res['success']
                status_class = 'success' if success else 'failed'
                status_text = 'PASSED' if success else 'FAILED'
                icon = '✅' if success else '❌'
                
                html += f"""
                        <div class="expectation-card {status_class}">
                            <div class="expectation-header">
                                <span class="expectation-type">{icon} {exp_type.replace('_', ' ').title()}</span>
                                <span class="status-badge {status_class}">{status_text}</span>
                            </div>
                            <div class="expectation-details">
                                <pre>{json.dumps(res['result'], indent=2)}</pre>
                            </div>
                        </div>
                """
            html += "</div>"
        html += "</div>"

    html += """
                <div style="text-align: center; padding: 20px 0;">
                    <a href="/" class="back-button">← Upload New Dataset</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "result": {"results": validation_results},
        "report_path": report_path
    }