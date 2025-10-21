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
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
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
    Generate business glossary using Claude API with three-layer definition structure
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

You are building a universal translator that works for claims adjusters, data engineers, and AI agents processing insurance data.

## Database Columns to Analyze:
{json.dumps(columns, indent=2)}
{clarifications_text}

## Your Task:

1. **Group related database columns** into abstract business terms
   - Do NOT create one-to-one mappings
   - Group similar columns (e.g., policy_number, pol_num, policy_id → "Policy Number")
   - Use standard insurance industry terminology

2. **For each business term, provide a THREE-LAYER DEFINITION**:

### Layer 1: Business Definition (Required, 1-2 sentences)
- Plain language explanation understandable to non-technical stakeholders
- Start with what the term IS before explaining what it does
- Use consistent patterns:
  * Person/Entity: "The [person/organization] who/that [role/function]..."
  * Date: "The date when [specific event occurs]..."
  * Amount: "The [monetary value/quantity] of [what it measures]..."
  * Status: "The current state of [entity] indicating [meaning]..."
- NO circular definitions (e.g., "Premium Amount: The amount of the premium")
- NO undefined acronyms

### Layer 2: Business Context (Required, 2-3 sentences)
- Why does this matter? How is it used in business processes?
- What decisions depend on it?
- Include relationships to other concepts
- Include cardinality when relevant (one-to-one, one-to-many, etc.)
- Distinguish between events (real-world) and records (system entries)
- For temporal data, be explicit about "as of when"

### Layer 3: Technical Bridge (Optional, 1-2 sentences)
- Only include if the term is frequently used in technical work
- Format: "Stored in [TABLE.COLUMN]. Related to [OTHER_TABLES]."
- Note whether values are stored directly or calculated

3. **Additional Fields**:
- **Synonyms**: List alternative terms (if applicable)
- **Allowed Values**: For coded/status fields, list valid values
- **Data Domain**: One of these 8 insurance domains:
  * Claims: Data related to insurance claims, settlements, adjustments
  * Policy: Information about policies, coverage, premiums
  * Risk: Risk assessment, underwriting, exposures
  * Customer: Personal and business information about policyholders
  * Broker: Information about brokers and their relationships
  * Agent: Data about agents, performance, relationships
  * Finance: Financial data, payments, accounting, billing
  * HR: Human resources, employees, payroll

## Quality Checklist - Ensure Each Definition:
✓ First sentence understandable to non-insurance person
✓ No circular definitions
✓ No unexplained acronyms
✓ Terms defined without requiring other term lookups first
✓ Scope and boundaries are clear
✓ Dates specify exactly which event they represent
✓ Relationships and cardinality mentioned when relevant

## Example Output Format:

{{
  "business_term": "Deductible",
  "business_definition": "The amount a policyholder must pay out-of-pocket before insurance coverage begins paying for a covered loss.",
  "business_context": "Deductibles help control insurance costs by having policyholders share in smaller losses. Higher deductibles typically result in lower premiums. The deductible is applied per claim or per policy period depending on policy terms.",
  "technical_bridge": "Stored in POLICY.DEDUCTIBLE_AMT. Related to CLAIM.DEDUCTIBLE_APPLIED which tracks the portion used for each claim.",
  "synonyms": ["Out-of-pocket minimum"],
  "allowed_values": null,
  "data_domain": "Policy",
  "associated_columns": "deductible|deductible_amt|ded_amt"
}}

Return the results as a JSON array with these exact keys:
- business_term (string)
- business_definition (string, required)
- business_context (string, required)
- technical_bridge (string or null)
- synonyms (array of strings, empty array if none)
- allowed_values (array of strings or null, for coded fields)
- data_domain (string, one of the 8 domains)
- associated_columns (string, pipe-separated)

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
    """Generate sample insurance glossary with three-layer structure"""
    return [
        {
            "business_term": "Policy Number",
            "business_definition": "The unique identifier assigned to each insurance policy for tracking and reference throughout its lifecycle.",
            "business_context": "Each policy must have exactly one policy number, which is used across all systems for claims processing, premium billing, and customer service. The policy number remains constant even if the policy is renewed or modified. It serves as the primary key for linking all policy-related transactions and documents.",
            "technical_bridge": "Stored in POLICY.POLICY_NUMBER. Referenced by CLAIM.POLICY_NUMBER and PAYMENT.POLICY_NUMBER as foreign keys.",
            "synonyms": ["Policy ID", "Contract Number"],
            "allowed_values": None,
            "data_domain": "Policy",
            "associated_columns": "policy_number|pol_num|policy_id|pol_no"
        },
        {
            "business_term": "Claim Amount",
            "business_definition": "The monetary value of a claim representing the total amount requested or approved for payment to cover a policyholder's covered loss.",
            "business_context": "The claim amount is determined by adjusters based on policy terms, deductibles, and coverage limits. It may be paid in a single settlement or multiple payments over time. The amount cannot exceed the policy's coverage limit minus any applicable deductible. This amount drives financial reserves and impacts loss ratio calculations.",
            "technical_bridge": "Stored in CLAIM.CLAIM_AMOUNT. Related to PAYMENT.PAYMENT_AMOUNT which tracks individual disbursements. May differ from CLAIM.RESERVE_AMOUNT which is the estimated liability.",
            "synonyms": ["Settlement Amount", "Claim Payment", "Loss Amount"],
            "allowed_values": None,
            "data_domain": "Claims",
            "associated_columns": "claim_amount|claim_amt|settlement_amount|paid_amount"
        },
        {
            "business_term": "Premium Amount",
            "business_definition": "The total amount charged to the policyholder for insurance coverage over a specified period.",
            "business_context": "Premiums are calculated based on underwriting risk assessment, coverage limits, deductibles, and policy term. They can be paid in full annually or in installments (monthly, quarterly, semi-annually). The premium amount is the primary revenue source for insurance operations and must be sufficient to cover expected claims, expenses, and profit margin.",
            "technical_bridge": "Stored in POLICY.PREMIUM_AMOUNT for annual premium or BILLING.INSTALLMENT_AMOUNT for payment plans. Related to PAYMENT.RECEIVED_AMOUNT for tracking payments.",
            "synonyms": ["Insurance Premium", "Policy Premium", "Premium Charge"],
            "allowed_values": None,
            "data_domain": "Finance",
            "associated_columns": "premium_amount|premium_amt|policy_premium|prem_amt"
        },
        {
            "business_term": "Policy Status",
            "business_definition": "The current state of an insurance policy indicating whether coverage is active, suspended, or terminated.",
            "business_context": "Policy status changes throughout the policy lifecycle based on premium payment, expiration, or policyholder actions. Only policies with 'active' status provide coverage and are eligible for claims. Status transitions require approval workflows and trigger billing, notification, and reporting processes.",
            "technical_bridge": "Stored in POLICY.STATUS. Status changes are logged in POLICY_HISTORY with timestamps and reason codes.",
            "synonyms": ["Coverage Status", "Policy State"],
            "allowed_values": ["active", "pending", "lapsed", "cancelled", "expired", "suspended"],
            "data_domain": "Policy",
            "associated_columns": "policy_status|status|policy_state|coverage_status"
        },
        {
            "business_term": "Loss Ratio",
            "business_definition": "The percentage of premium income paid out as claims, calculated as total claims divided by total premiums earned.",
            "business_context": "Loss ratio is a key profitability metric used to evaluate underwriting performance and pricing adequacy. A ratio above 100% indicates underwriting losses where claims exceed premiums. Insurance companies monitor loss ratios by product line, region, and time period to identify trends and adjust pricing strategies.",
            "technical_bridge": "Calculated field: SUM(CLAIM.CLAIM_AMOUNT) / SUM(POLICY.EARNED_PREMIUM) * 100. Not stored directly but computed for reporting periods.",
            "synonyms": ["Claims Ratio", "Loss Cost Ratio"],
            "allowed_values": None,
            "data_domain": "Finance",
            "associated_columns": "loss_ratio|claims_ratio|loss_pct"
        }
    ]

def create_xlsx_file(glossary_data: List[Dict[str, Any]], filename: str) -> str:
    """
    Create Excel file with glossary data using three-layer structure
    Returns: filepath to the created XLSX file
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Business_Glossary"

    # Define headers
    headers = [
        "Business Term",
        "Business Definition",
        "Business Context",
        "Technical Bridge",
        "Synonyms",
        "Allowed Values",
        "Data Domain",
        "Associated Database Columns"
    ]

    # Style for headers
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Border style
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # Write data
    for row_num, entry in enumerate(glossary_data, 2):
        # Business Term
        cell = ws.cell(row=row_num, column=1)
        cell.value = entry.get('business_term', '')
        cell.font = Font(bold=True, size=10)
        cell.border = thin_border

        # Business Definition
        cell = ws.cell(row=row_num, column=2)
        cell.value = entry.get('business_definition', '')
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.border = thin_border

        # Business Context
        cell = ws.cell(row=row_num, column=3)
        cell.value = entry.get('business_context', '')
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.border = thin_border

        # Technical Bridge
        cell = ws.cell(row=row_num, column=4)
        cell.value = entry.get('technical_bridge', '') or 'N/A'
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.border = thin_border

        # Synonyms
        cell = ws.cell(row=row_num, column=5)
        synonyms = entry.get('synonyms', [])
        cell.value = ', '.join(synonyms) if synonyms else 'N/A'
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.border = thin_border

        # Allowed Values
        cell = ws.cell(row=row_num, column=6)
        allowed_values = entry.get('allowed_values', None)
        cell.value = ', '.join(allowed_values) if allowed_values else 'N/A'
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.border = thin_border

        # Data Domain
        cell = ws.cell(row=row_num, column=7)
        cell.value = entry.get('data_domain', '')
        cell.border = thin_border

        # Associated Columns
        cell = ws.cell(row=row_num, column=8)
        cell.value = entry.get('associated_columns', '')
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.border = thin_border

    # Set column widths
    ws.column_dimensions['A'].width = 20  # Business Term
    ws.column_dimensions['B'].width = 50  # Business Definition
    ws.column_dimensions['C'].width = 60  # Business Context
    ws.column_dimensions['D'].width = 50  # Technical Bridge
    ws.column_dimensions['E'].width = 25  # Synonyms
    ws.column_dimensions['F'].width = 30  # Allowed Values
    ws.column_dimensions['G'].width = 15  # Data Domain
    ws.column_dimensions['H'].width = 40  # Associated Columns

    # Set row height for header
    ws.row_dimensions[1].height = 30

    # Freeze header row
    ws.freeze_panes = "A2"

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
