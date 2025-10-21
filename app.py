from flask import Flask, render_template, request, jsonify
import os
import json
import csv
import pandas as pd
from werkzeug.utils import secure_filename
import re
from typing import List, Dict, Any
import anthropic

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'csv', 'xlsx', 'xls', 'json'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def parse_file(filepath):
    """Parse uploaded file and extract line items for glossary generation"""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    try:
        if ext == '.csv':
            df = pd.read_csv(filepath)
            # Extract line items from the dataframe
            return extract_line_items_from_dataframe(df)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
            # Extract line items from the dataframe
            return extract_line_items_from_dataframe(df)
        elif ext == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        elif ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None

def extract_line_items_from_dataframe(df):
    """
    Extract line items from a dataframe for glossary generation.
    Assumes the file contains business terms as rows with columns like:
    - Term/Title/Name (the business term)
    - Description/Definition (explanation)
    - Other metadata columns
    """
    if df.empty:
        return "No data found in file"

    # Convert dataframe to a structured text format
    result = []

    # Get column names
    columns = df.columns.tolist()

    # Iterate through rows and format them as line items
    for idx, row in df.iterrows():
        item_parts = []
        for col in columns:
            value = row[col]
            if pd.notna(value):  # Only include non-null values
                item_parts.append(f"{col}: {value}")

        if item_parts:
            result.append("\n".join(item_parts))

    return "\n\n---\n\n".join(result)

def generate_glossary(file_content: str, business_context: str) -> List[Dict[str, Any]]:
    """
    Generate business glossary using Claude API
    """
    # Check if ANTHROPIC_API_KEY is set
    api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        # Fallback to sample data if API key is not available
        return generate_sample_glossary(business_context)

    try:
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""You are a business analyst expert specializing in {business_context}.

Analyze the following data containing business terms and metrics. Each item in the data represents a business term or metric.
Create a comprehensive business glossary by enriching and standardizing each term.

For each term or metric in the data, provide:
1. Title: The name of the business term or metric (extract from the data)
2. Description: Clear, professional explanation of what it means (enhance if provided, or create if missing)
3. Examples: Concrete examples of the term/metric in use (extract from data or generate relevant ones)
4. Business Logic: The business rules or logic associated with it
5. Data Type: The data type (string, number, date, boolean, currency, etc.)
6. Technical Aliases: Alternative technical names or database column names
7. Synonyms: Other business names for the same concept
8. Logical Formula: (For metrics only) The calculation formula

IMPORTANT: Extract business terms from the LINE ITEMS in the data, not from column headers.
Each line item represents a separate business term or concept.

Data content:
{file_content[:8000]}

Please return the results in JSON format as an array of objects with these exact keys:
- title
- description
- examples
- business_logic
- data_type
- technical_aliases
- synonyms
- logical_formula (empty string if not a metric)

Return ONLY the JSON array, no additional text."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
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
        return generate_sample_glossary(business_context)

def generate_sample_glossary(business_context: str) -> List[Dict[str, Any]]:
    """Generate sample glossary data based on business context"""

    glossaries = {
        "General Insurance": [
            {
                "title": "Premium",
                "description": "The amount paid by the policyholder to the insurance company for coverage",
                "examples": "Monthly premium: $150, Annual premium: $1,800",
                "business_logic": "Calculated based on risk factors, coverage amount, and policy term",
                "data_type": "Currency/Decimal",
                "technical_aliases": "premium_amount, policy_premium, prem_amt",
                "synonyms": "Insurance Premium, Policy Payment",
                "logical_formula": ""
            },
            {
                "title": "Claim Amount",
                "description": "The monetary value requested or paid for an insurance claim",
                "examples": "Claim for vehicle damage: $5,000, Medical claim: $2,500",
                "business_logic": "Must not exceed policy coverage limits; subject to deductibles",
                "data_type": "Currency/Decimal",
                "technical_aliases": "claim_amt, paid_amount, settlement_amount",
                "synonyms": "Settlement Amount, Claim Payment, Payout",
                "logical_formula": ""
            },
            {
                "title": "Loss Ratio",
                "description": "The ratio of claims paid to premiums earned",
                "examples": "Loss Ratio of 0.75 means 75% of premiums are paid out as claims",
                "business_logic": "Used to measure profitability and pricing adequacy of insurance products",
                "data_type": "Decimal/Percentage",
                "technical_aliases": "loss_ratio, claims_ratio",
                "synonyms": "Claims Ratio, Incurred Loss Ratio",
                "logical_formula": "(Total Claims Paid / Total Premiums Earned) * 100"
            }
        ],
        "Life Insurance": [
            {
                "title": "Sum Assured",
                "description": "The guaranteed amount payable to beneficiaries upon death or maturity",
                "examples": "Life cover: $500,000, Term insurance sum assured: $1,000,000",
                "business_logic": "Determined at policy inception based on income, needs, and underwriting",
                "data_type": "Currency/Decimal",
                "technical_aliases": "coverage_amount, death_benefit, face_amount",
                "synonyms": "Death Benefit, Coverage Amount, Face Value",
                "logical_formula": ""
            },
            {
                "title": "Surrender Value",
                "description": "The amount payable to the policyholder if the policy is terminated before maturity",
                "examples": "After 5 years, surrender value: $12,000",
                "business_logic": "Calculated based on premiums paid, policy duration, and surrender charges",
                "data_type": "Currency/Decimal",
                "technical_aliases": "cash_surrender_value, csv, surrender_amt",
                "synonyms": "Cash Value, Termination Value",
                "logical_formula": "Total Premiums Paid - Surrender Charges - Policy Fees"
            },
            {
                "title": "Mortality Rate",
                "description": "The probability of death within a specified age group",
                "examples": "Mortality rate for age 40-45: 0.002 (0.2%)",
                "business_logic": "Used for premium calculation and reserves estimation",
                "data_type": "Decimal/Percentage",
                "technical_aliases": "death_rate, mortality_prob",
                "synonyms": "Death Rate, Mortality Probability",
                "logical_formula": "Number of Deaths / Total Population in Age Group"
            }
        ],
        "Information Technology": [
            {
                "title": "User ID",
                "description": "Unique identifier assigned to each system user",
                "examples": "U123456, user@example.com, EMP001",
                "business_logic": "Must be unique across the system; used for authentication and audit trails",
                "data_type": "String/VARCHAR",
                "technical_aliases": "user_id, uid, username, login_id",
                "synonyms": "Username, Login ID, Account ID",
                "logical_formula": ""
            },
            {
                "title": "Session Duration",
                "description": "The length of time a user remains actively logged into the system",
                "examples": "Average session: 45 minutes, Timeout: 30 minutes",
                "business_logic": "Tracked for security and usage analytics; sessions expire after inactivity",
                "data_type": "Integer/Time",
                "technical_aliases": "session_time, login_duration, active_time",
                "synonyms": "Login Duration, Active Time, Session Length",
                "logical_formula": ""
            },
            {
                "title": "System Uptime",
                "description": "Percentage of time the system is operational and accessible",
                "examples": "99.9% uptime, 99.99% availability",
                "business_logic": "Calculated excluding planned maintenance; key SLA metric",
                "data_type": "Percentage/Decimal",
                "technical_aliases": "availability, uptime_pct, system_availability",
                "synonyms": "Availability, Service Uptime, System Availability",
                "logical_formula": "(Total Time - Downtime) / Total Time * 100"
            }
        ]
    }

    return glossaries.get(business_context, glossaries["Information Technology"])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    business_context = request.form.get('business_context', 'Information Technology')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Parse the file
        file_content = parse_file(filepath)

        if file_content is None:
            os.remove(filepath)
            return jsonify({'error': 'Failed to parse file'}), 400

        # Generate glossary
        glossary = generate_glossary(file_content, business_context)

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'glossary': glossary,
            'context': business_context
        })

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
