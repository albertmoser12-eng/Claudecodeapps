from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import csv
import pandas as pd
from werkzeug.utils import secure_filename
import re
from typing import List, Dict, Any, Tuple
import anthropic
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'csv', 'xlsx', 'xls', 'json'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Insurance domain classifications
INSURANCE_DOMAINS = [
    "Claims", "Policy", "Risk", "Customer", "Broker",
    "Agent", "Finance", "HR"
]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_column_names(filepath) -> List[str]:
    """Extract database column names from uploaded file"""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    try:
        if ext == '.csv':
            df = pd.read_csv(filepath, nrows=0)  # Read only headers
            return df.columns.tolist()
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath, nrows=0)  # Read only headers
            return df.columns.tolist()
        elif ext == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return list(data[0].keys())
                elif isinstance(data, dict):
                    return list(data.keys())
                return []
        elif ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                # Assume each line is a column name
                return [line.strip() for line in f.readlines() if line.strip()]
        else:
            return []
    except Exception as e:
        print(f"Error extracting column names: {e}")
        return []

def deduplicate_columns(columns: List[str]) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Deduplicate column names and group similar ones.
    Returns: (deduplicated_list, duplicates_map)
    """
    seen = {}
    deduplicated = []
    duplicates_map = {}

    for col in columns:
        # Normalize the column name for comparison
        normalized = col.lower().replace('_', '').replace('-', '').replace(' ', '')

        if normalized not in seen:
            seen[normalized] = col
            deduplicated.append(col)
        else:
            # Track duplicates
            original = seen[normalized]
            if original not in duplicates_map:
                duplicates_map[original] = []
            duplicates_map[original].append(col)

    return deduplicated, duplicates_map

def identify_abbreviations(columns: List[str]) -> List[Dict[str, Any]]:
    """
    Identify abbreviations that might need clarification.
    Returns list of abbreviations with possible meanings.
    """
    # Common insurance abbreviations that might be ambiguous
    ambiguous_abbrevs = {
        'POL': ['Policy', 'Police', 'Pollution'],
        'CLM': ['Claim', 'Column'],
        'AGT': ['Agent', 'Agreement'],
        'CUST': ['Customer', 'Custody', 'Customization'],
        'AMT': ['Amount'],
        'NUM': ['Number'],
        'ID': ['Identifier', 'Identity'],
        'DT': ['Date', 'Data Type'],
        'TYP': ['Type'],
        'STS': ['Status'],
        'PCT': ['Percent', 'Percentage'],
        'CNT': ['Count'],
        'IND': ['Indicator', 'Individual', 'Index'],
        'REF': ['Reference', 'Refund'],
        'PREM': ['Premium', 'Preliminary'],
        'DEDUCT': ['Deductible', 'Deduction'],
        'COV': ['Coverage', 'Covenant'],
        'LIAB': ['Liability'],
        'BENEF': ['Beneficiary', 'Benefit'],
        'ADDR': ['Address'],
        'TEL': ['Telephone', 'Telegram'],
        'EMP': ['Employee', 'Employer', 'Empty'],
        'DEPT': ['Department', 'Deposit'],
        'DIV': ['Division', 'Dividend'],
        'PROD': ['Product', 'Production'],
        'COMM': ['Commission', 'Communication', 'Commercial']
    }

    clarifications_needed = []

    for col in columns:
        # Split by common delimiters
        parts = re.split(r'[_\-\s.]+', col.upper())

        for part in parts:
            if part in ambiguous_abbrevs and len(ambiguous_abbrevs[part]) > 1:
                # Check if we already added this abbreviation
                if not any(c['abbreviation'] == part for c in clarifications_needed):
                    clarifications_needed.append({
                        'abbreviation': part,
                        'possible_meanings': ambiguous_abbrevs[part],
                        'example_columns': [c for c in columns if part in c.upper()][:3]
                    })

    return clarifications_needed

def generate_glossary_with_claude(columns: List[str], abbreviation_clarifications: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Generate business glossary using Claude API following the 6-step process
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        return generate_sample_insurance_glossary()

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Format abbreviation clarifications
        clarifications_text = ""
        if abbreviation_clarifications:
            clarifications_text = "\n\nAbbreviation Clarifications Provided by User:\n"
            for abbrev, meaning in abbreviation_clarifications.items():
                clarifications_text += f"- {abbrev}: {meaning}\n"

        prompt = f"""You are an expert insurance data analyst creating a comprehensive business glossary from database column names.

Follow these steps systematically:

## Step 1: Data Preparation and Deduplication
The column names have already been deduplicated. Here are the database columns to analyze:
{json.dumps(columns, indent=2)}
{clarifications_text}

## Step 2-6: Generate Business Glossary

Your task is to:
1. Review the database column names
2. Classify each column into one of these 8 insurance data domains:
   - **Claims**: Data related to insurance claims, settlements, adjustments, and claim processing
   - **Policy**: Information about insurance policies, coverage, premiums, and policy administration
   - **Risk**: Data concerning risk assessment, underwriting, exposures, and risk management
   - **Customer**: Personal and business information about policyholders and insureds
   - **Broker**: Information about insurance brokers, their relationships, and transactions
   - **Agent**: Data about insurance agents, their performance, and client relationships
   - **Finance**: Financial data including payments, accounting, billing, and financial reporting
   - **HR**: Human resources data for employees, payroll, and organizational structure

3. Create ABSTRACT BUSINESS TERMS by grouping related database columns:
   - **Do NOT create one-to-one mappings** between columns and business terms
   - Instead, group related columns under broader business concepts
   - Use standard insurance industry terminology
   - Focus on business meaning, not technical implementation

4. For each business term, provide:
   - **Business Term**: Clear, concise insurance industry term (use natural language, 2-4 words)
   - **Description**: Business-focused definition (maximum 50 words) explaining the concept's relevance to insurance operations
   - **Data Domain**: One of the 8 specified domains
   - **Associated Database Columns**: List of database columns that relate to this business term (pipe-separated)

## Quality Standards:
- Descriptions must be business-friendly, avoiding technical jargon
- Focus on "what" and "why" rather than "how"
- Use active voice and clear language
- Ensure consistency in terminology across all entries
- Group related columns together (e.g., policy_number, pol_num, policy_id → "Policy Number")

Return the results in JSON format as an array of objects with these exact keys:
- business_term
- description
- data_domain
- associated_columns (pipe-separated string)

Return ONLY the JSON array, no additional text."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text

        # Try to extract JSON from the response
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            glossary_data = json.loads(json_match.group())
            return glossary_data
        else:
            return json.loads(response_text)

    except Exception as e:
        print(f"Error generating glossary with Claude: {e}")
        return generate_sample_insurance_glossary()

def generate_sample_insurance_glossary() -> List[Dict[str, Any]]:
    """Generate sample insurance glossary when API is not available"""
    return [
        {
            "business_term": "Policy Number",
            "description": "Unique identifier assigned to each insurance policy for tracking, reference, and transaction processing across all insurance operations and systems.",
            "data_domain": "Policy",
            "associated_columns": "policy_number|pol_num|policy_id|pol_no"
        },
        {
            "business_term": "Claim Amount",
            "description": "The monetary value of a claim representing the policyholder's requested or approved payment for a covered loss, subject to deductibles and coverage limits.",
            "data_domain": "Claims",
            "associated_columns": "claim_amount|claim_amt|settlement_amount|paid_amount"
        },
        {
            "business_term": "Premium Amount",
            "description": "The total premium charged to the policyholder for insurance coverage, calculated based on risk assessment, coverage limits, and policy term.",
            "data_domain": "Finance",
            "associated_columns": "premium_amount|premium_amt|policy_premium|prem_amt"
        },
        {
            "business_term": "Customer Information",
            "description": "Personal and business information about policyholders including names, addresses, contact details, and identification numbers.",
            "data_domain": "Customer",
            "associated_columns": "customer_name|cust_name|customer_id|cust_address|customer_phone"
        },
        {
            "business_term": "Loss Ratio",
            "description": "Key profitability metric measuring the proportion of premium income paid out as claims, indicating underwriting performance and pricing adequacy.",
            "data_domain": "Finance",
            "associated_columns": "loss_ratio|claims_ratio|loss_pct"
        }
    ]

def create_xlsx_file(glossary_data: List[Dict[str, Any]], filename: str) -> str:
    """
    Create Excel file with glossary data following specifications
    Returns: filepath to the created XLSX file
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Business_Glossary"

    # Define headers
    headers = ["Business Term", "Description", "Data Domain", "Associated Database Columns"]

    # Style for headers
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

    # Write data
    for row_num, entry in enumerate(glossary_data, 2):
        ws.cell(row=row_num, column=1).value = entry.get('business_term', '')
        ws.cell(row=row_num, column=2).value = entry.get('description', '')
        ws.cell(row=row_num, column=3).value = entry.get('data_domain', '')
        ws.cell(row=row_num, column=4).value = entry.get('associated_columns', '')

        # Wrap text for description column
        ws.cell(row=row_num, column=2).alignment = Alignment(wrap_text=True, vertical="top")

    # Auto-fit column widths
    for col_num, header in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        if col_num == 2:  # Description column
            ws.column_dimensions[column_letter].width = 60
        elif col_num == 4:  # Associated Columns
            ws.column_dimensions[column_letter].width = 40
        else:
            ws.column_dimensions[column_letter].width = 20

    # Freeze header row
    ws.freeze_panes = "A2"

    # Add data validation for Data Domain column (optional, for reference)
    # Note: This doesn't add dropdown in existing cells, but sets validation

    # Save file
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    wb.save(output_path)

    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Step 1: Upload file and return deduplicated columns with abbreviations"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract column names
        columns = extract_column_names(filepath)

        if not columns:
            os.remove(filepath)
            return jsonify({'error': 'No columns found in file'}), 400

        # Deduplicate
        deduplicated_columns, duplicates_map = deduplicate_columns(columns)

        # Identify abbreviations needing clarification
        abbreviations = identify_abbreviations(deduplicated_columns)

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'columns': deduplicated_columns,
            'total_columns': len(columns),
            'deduplicated_count': len(deduplicated_columns),
            'duplicates_removed': len(columns) - len(deduplicated_columns),
            'abbreviations': abbreviations,
            'duplicates_map': duplicates_map
        })

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/generate', methods=['POST'])
def generate_glossary():
    """Step 2: Generate glossary with abbreviation clarifications"""
    data = request.json
    columns = data.get('columns', [])
    abbreviation_clarifications = data.get('clarifications', {})

    if not columns:
        return jsonify({'error': 'No columns provided'}), 400

    # Generate glossary
    glossary = generate_glossary_with_claude(columns, abbreviation_clarifications)

    # Sort by business term
    glossary = sorted(glossary, key=lambda x: x.get('business_term', ''))

    return jsonify({
        'success': True,
        'glossary': glossary,
        'total_terms': len(glossary)
    })

@app.route('/download', methods=['POST'])
def download_glossary():
    """Step 3: Create and download XLSX file"""
    data = request.json
    glossary = data.get('glossary', [])

    if not glossary:
        return jsonify({'error': 'No glossary data provided'}), 400

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"Insurance_Business_Glossary_{timestamp}.xlsx"

    # Create XLSX file
    try:
        filepath = create_xlsx_file(glossary, filename)

        # Send file
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"Error creating XLSX file: {e}")
        return jsonify({'error': 'Failed to create XLSX file'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
