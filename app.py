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

CRITICAL REQUIREMENTS FOR EACH FIELD:

1. Title: The name of the business term or metric (extract from the data)

2. Description: Focus on SEMANTIC MEANING and PURPOSE. Explain:
   - What the term IS (its definition)
   - What it measures or represents
   - How it's used in business operations
   - Why it matters
   AVOID generic phrases like "Business term representing..." or "Used in the {business_context} domain"
   GOOD EXAMPLE: "The total number of vendors is the count of vendors with unique vendor ID and is used to analyze and monitor relationships and data completeness with third-party providers"
   BAD EXAMPLE: "Business term representing vendor information in the General Insurance domain"

3. Examples: Provide ACTUAL DATA VALUES that would appear in a database:
   - For counts/numbers: Use realistic values like "2,500" or "15,342"
   - For status fields: Use actual status values like "active", "inactive", "pending"
   - For dates: Use realistic date formats like "2024-01-15", "2023-12-31"
   - For amounts: Use real currency values like "$150,000", "$2,500.00"
   - For IDs: Use representative formats like "VNDR-00123", "POL-2024-001"
   GOOD EXAMPLE: "2,500" or "active, inactive, suspended"
   BAD EXAMPLE: "High number of vendors" or "Various status values"

4. Business Logic: Provide SPECIFIC VALIDATION RULES and business constraints:
   - Data validation rules (e.g., "Must be greater than 0", "Must be unique")
   - Relationship rules (e.g., "End date must be after start date")
   - Business constraints (e.g., "Cannot exceed coverage limit", "Required when policy is active")
   - Calculation dependencies (e.g., "Depends on premium amount and coverage period")
   AVOID generic statements like "Governed by business rules" or "Subject to data quality standards"
   GOOD EXAMPLE: "Contract end date must be after contract start date; minimum contract duration is 30 days"
   BAD EXAMPLE: "Governed by General Insurance business rules and data quality standards"

5. Data Type: The technical data type (string, integer, decimal, date, boolean, currency, etc.)

6. Technical Aliases: Alternative technical names or database column names (pipe-separated)
   EXAMPLE: "vendor_count|total_vendors|vndr_cnt"

7. Synonyms: Other business names for the same concept (pipe-separated)
   EXAMPLE: "Supplier Count|Provider Total|Third-Party Count"

8. Logical Formula: For metrics, include ACTUAL ELEMENTS from the title/description:
   - Reference specific fields or tables
   - Use clear calculation notation
   - Include aggregation functions where appropriate
   GOOD EXAMPLE: "Count(VendorID)" for "Total number of vendors"
   GOOD EXAMPLE: "SUM(ClaimAmount) / SUM(Premium) * 100" for "Loss Ratio"
   BAD EXAMPLE: "Calculated based on vendor data"

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
                "title": "Premium Amount",
                "description": "The total premium charged to the policyholder for insurance coverage, calculated based on underwriting risk assessment, coverage limits, deductibles, and policy term. This amount represents the insurer's pricing for accepting the covered risks and is the primary revenue source for insurance operations.",
                "examples": "$1,250.00, $3,450.50, $875.25",
                "business_logic": "Must be greater than $0; cannot be modified after policy issuance without underwriting approval; annual premium must equal sum of installment payments if payment plan selected",
                "data_type": "Decimal(10,2)",
                "technical_aliases": "premium_amount|policy_premium|prem_amt|charged_premium",
                "synonyms": "Policy Premium|Insurance Premium|Premium Charge",
                "logical_formula": ""
            },
            {
                "title": "Claim Amount",
                "description": "The monetary value of a claim representing the policyholder's requested or approved payment for a covered loss. This amount is assessed by claims adjusters against policy terms and is subject to deductibles, coverage limits, and policy exclusions to determine the final settlement payment.",
                "examples": "$5,250.00, $15,000.00, $2,450.75",
                "business_logic": "Must be greater than $0; cannot exceed policy coverage limit minus deductible; requires supporting documentation for amounts over $10,000; must be validated against policy effective dates",
                "data_type": "Decimal(12,2)",
                "technical_aliases": "claim_amt|paid_amount|settlement_amount|loss_amount",
                "synonyms": "Settlement Amount|Claim Payment|Loss Payment",
                "logical_formula": ""
            },
            {
                "title": "Loss Ratio",
                "description": "A key profitability metric measuring the proportion of premium income paid out as claims, calculated as total incurred losses divided by earned premiums. Insurance companies use this metric to evaluate underwriting performance, pricing adequacy, and overall portfolio profitability. A loss ratio above 100% indicates underwriting losses.",
                "examples": "0.67, 0.85, 1.12",
                "business_logic": "Must be greater than or equal to 0; values above 1.0 indicate unprofitable underwriting; calculated monthly and year-to-date; excludes acquisition costs and operating expenses",
                "data_type": "Decimal(5,4)",
                "technical_aliases": "loss_ratio|claims_ratio|incurred_loss_ratio",
                "synonyms": "Claims Ratio|Loss Cost Ratio",
                "logical_formula": "SUM(ClaimAmount) / SUM(EarnedPremium)"
            },
            {
                "title": "Policy Status",
                "description": "The current state of an insurance policy indicating whether coverage is active, suspended, or terminated. This status determines billing requirements, coverage validity, and claim eligibility, and changes based on payment status, expiration dates, and policyholder actions.",
                "examples": "active, lapsed, cancelled, expired",
                "business_logic": "Must be one of predefined values: active, pending, lapsed, cancelled, expired; only 'active' policies provide coverage; status changes require approval workflow; cannot change from cancelled to active without new underwriting",
                "data_type": "String/VARCHAR(20)",
                "technical_aliases": "policy_status|status|policy_state|coverage_status",
                "synonyms": "Coverage Status|Policy State",
                "logical_formula": ""
            }
        ],
        "Life Insurance": [
            {
                "title": "Sum Assured",
                "description": "The guaranteed lump sum amount payable to designated beneficiaries upon the insured's death or at policy maturity for endowment plans. This amount is determined during policy inception through underwriting assessment and remains fixed throughout the policy term, serving as the foundation for premium calculation and representing the insurer's maximum liability under the contract.",
                "examples": "$500,000.00, $1,000,000.00, $250,000.00",
                "business_logic": "Must be at least $50,000 for individual policies; cannot exceed 20 times annual income for term insurance or 10 times for whole life; requires medical underwriting for amounts above $1,000,000; cannot be increased without new underwriting assessment",
                "data_type": "Decimal(12,2)",
                "technical_aliases": "sum_assured|coverage_amount|death_benefit|face_amount",
                "synonyms": "Death Benefit|Face Value|Coverage Amount",
                "logical_formula": ""
            },
            {
                "title": "Surrender Value",
                "description": "The cash amount payable to the policyholder if the policy is voluntarily terminated before its maturity date or the insured's death. This value accumulates over the policy term based on paid premiums, investment performance, and guaranteed returns, minus surrender charges, policy loans, and administrative fees. Only available after the policy has been in force for the minimum surrender period.",
                "examples": "$12,450.50, $28,900.00, $156,780.25",
                "business_logic": "Only available after minimum 3 years from policy inception; must be less than or equal to sum assured; reduces to zero if policy loans exceed surrender value; calculation excludes unpaid premiums and interest on loans; policy terminates upon surrender",
                "data_type": "Decimal(12,2)",
                "technical_aliases": "surrender_value|cash_surrender_value|csv|termination_value",
                "synonyms": "Cash Value|Termination Value|Policy Cash Value",
                "logical_formula": "SUM(PremiumPaid) - SurrenderCharges - PolicyFees - OutstandingLoans"
            },
            {
                "title": "Policy Term",
                "description": "The duration in years for which the life insurance policy provides coverage, starting from the policy commencement date and ending at the maturity date or term expiration. This period determines premium payment duration, coverage availability, and maturity benefit eligibility for endowment plans.",
                "examples": "10, 20, 25, 30",
                "business_logic": "Must be between 5 and 40 years; maximum term limited by insured age at maturity (typically age 75 or 80); term plus entry age cannot exceed maximum age limit; cannot be modified after policy issuance; determines premium calculation basis",
                "data_type": "Integer",
                "technical_aliases": "policy_term|term_years|coverage_period|policy_duration",
                "synonyms": "Coverage Period|Policy Duration|Insurance Term",
                "logical_formula": ""
            },
            {
                "title": "Persistency Ratio",
                "description": "A retention metric measuring the percentage of life insurance policies that remain active and in-force over a specified period, calculated by comparing active policies at period end to policies at period start. This metric indicates customer satisfaction, policy affordability, and portfolio quality, with higher ratios reflecting better business retention and profitability.",
                "examples": "0.88, 0.92, 0.85",
                "business_logic": "Must be between 0 and 1; calculated monthly, quarterly, and annually; excludes policies terminated due to maturity or death claims; includes only renewable policies; values below 0.80 trigger retention improvement initiatives",
                "data_type": "Decimal(4,4)",
                "technical_aliases": "persistency_ratio|retention_rate|policy_retention|continuation_ratio",
                "synonyms": "Retention Rate|Policy Continuation Ratio|Lapse Ratio Inverse",
                "logical_formula": "COUNT(ActivePolicies_EndPeriod) / COUNT(ActivePolicies_StartPeriod)"
            }
        ],
        "Information Technology": [
            {
                "title": "User ID",
                "description": "A unique alphanumeric identifier assigned to each registered system user for authentication, authorization, and audit trail purposes. This identifier serves as the primary key in the user management system and is used across all application modules to track user actions, enforce access controls, and maintain data security compliance.",
                "examples": "USR-000123, EMP-045678, user.john@example.com",
                "business_logic": "Must be unique across all users; cannot be null or empty; length between 6 and 50 characters; cannot be changed after creation; must persist even after user account deactivation for audit history; alphanumeric and special characters (@.-_) only",
                "data_type": "VARCHAR(50)",
                "technical_aliases": "user_id|uid|username|login_id|user_identifier",
                "synonyms": "Username|Login ID|User Identifier|Account ID",
                "logical_formula": ""
            },
            {
                "title": "Session Duration",
                "description": "The elapsed time in minutes between user login and logout (or timeout), measuring how long a user maintains an active authenticated session. This metric is critical for analyzing user engagement patterns, optimizing session timeout policies, and identifying potential security anomalies from abnormally long sessions.",
                "examples": "45, 120, 15, 240",
                "business_logic": "Must be greater than 0; maximum session duration is 480 minutes (8 hours); sessions exceeding 30 minutes of inactivity are automatically terminated; duration calculated only for successfully authenticated sessions; concurrent sessions from same user are tracked separately",
                "data_type": "Integer",
                "technical_aliases": "session_duration|session_time|login_duration|active_time_minutes",
                "synonyms": "Login Duration|Active Session Time|Session Length",
                "logical_formula": "DATEDIFF(minute, SessionStart, SessionEnd)"
            },
            {
                "title": "System Uptime Percentage",
                "description": "The percentage of time the application system is fully operational and accessible to users over a defined measurement period, calculated as total available time divided by total time excluding scheduled maintenance windows. This metric is a key Service Level Agreement (SLA) indicator measuring system reliability and is used to assess infrastructure performance and identify improvement opportunities.",
                "examples": "99.95, 99.87, 100.00, 99.50",
                "business_logic": "Must be between 0 and 100; calculated hourly, daily, and monthly; excludes planned maintenance windows documented in change management system; SLA target is 99.9% monthly; values below 99.5% trigger incident investigation; includes only production environment downtime",
                "data_type": "Decimal(5,2)",
                "technical_aliases": "uptime_pct|system_uptime|availability_pct|service_availability",
                "synonyms": "System Availability|Service Uptime|Availability Percentage",
                "logical_formula": "(TotalMinutes - UnplannedDowntimeMinutes) / TotalMinutes * 100"
            },
            {
                "title": "API Response Time",
                "description": "The time in milliseconds elapsed between receiving an API request and sending the complete response, measuring the performance and efficiency of API endpoints. This metric is monitored to ensure optimal user experience, identify performance bottlenecks, and maintain service level objectives for application responsiveness.",
                "examples": "125, 350, 89, 1250",
                "business_logic": "Must be greater than 0; target response time is under 200ms for 95th percentile; responses exceeding 2000ms (2 seconds) trigger performance alerts; measured at application layer excluding network latency; calculated only for successful HTTP 200 responses; aggregated by endpoint and time period",
                "data_type": "Integer",
                "technical_aliases": "response_time_ms|api_latency|request_duration|api_response_time",
                "synonyms": "API Latency|Response Time|Request Duration|Endpoint Performance",
                "logical_formula": "ResponseTimestamp - RequestTimestamp"
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
