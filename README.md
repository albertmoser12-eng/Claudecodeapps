# Business Glossary Generator

A web application that automatically generates comprehensive business glossaries from uploaded data files. The app uses AI to parse documents and extract business terms, metrics, and their detailed attributes.

## Two Versions Available

This project provides **two versions** of the Business Glossary Generator:

### 1. Standalone HTML Version (No Installation Required)
📄 **File**: `business-glossary-generator.html`

- **Zero installation** - just open in any web browser
- Works **completely offline** - no server needed
- **100% private** - all processing happens locally
- Supports CSV, JSON, and TXT files
- Perfect for quick analysis or sharing the tool

👉 [See HTML Version Documentation](HTML_VERSION_README.md)

### 2. Flask Web Application (Full-Featured)
🚀 **Files**: `app.py`, `templates/`, `static/`

- Full Python Flask backend
- Supports **Excel files** (.xlsx, .xls)
- **AI-powered** analysis with Claude API
- More advanced features and customization
- Can be deployed as a web service

👉 Continue reading below for Flask version setup

---

## Features

- **File Upload Support**: Accepts multiple file formats (CSV, Excel, TXT, JSON)
- **Business Context Selection**: Choose from General Insurance, Life Insurance, or Information Technology domains
- **AI-Powered Analysis**: Automatically extracts and categorizes business terms and metrics
- **Comprehensive Output**: Generates glossary with 8 detailed columns:
  - Title
  - Description
  - Examples
  - Business Logic
  - Data Type
  - Technical Aliases
  - Synonyms
  - Logical Formula (for metrics)
- **Export Functionality**: Download results as CSV
- **Modern UI**: Clean, responsive design with drag-and-drop file upload

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Claudecodeapps
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Set up Claude API for enhanced AI generation:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```
Note: If no API key is provided, the app will use sample glossaries based on the selected business context.

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Using the application:
   - Select a business context from the dropdown (General Insurance, Life Insurance, or Information Technology)
   - Upload a file containing your business data (CSV, Excel, TXT, or JSON)
   - Click "Generate Glossary" to process the file
   - View the generated glossary table with all extracted terms and metrics
   - Export results to CSV if needed

## Input File Format

The application generates glossaries from **line items** in your uploaded files, where each row/item represents a business term or metric to be included in the glossary.

### CSV Example (Recommended Format)
```csv
Term,Description,Examples,Data Type
Premium,Amount paid for insurance coverage,Monthly: $150; Annual: $1800,Currency/Decimal
Claim Amount,Monetary value of insurance claim,Auto claim: $5000,Currency/Decimal
Loss Ratio,Ratio of claims paid to premiums earned,75% loss ratio,Percentage
```

Each row represents a business term. Columns can include:
- **Term/Title/Name**: The business term (required)
- **Description/Definition**: Explanation of the term
- **Examples**: Sample values or use cases
- **Data Type**: Technical data type
- **Technical Aliases**: Alternative names
- **Synonyms**: Business synonyms
- **Logical Formula**: Calculation formula (for metrics)

### JSON Example
```json
[
  {
    "term": "Premium",
    "description": "Amount paid for insurance coverage",
    "examples": "Monthly: $150; Annual: $1800",
    "data_type": "Currency/Decimal"
  },
  {
    "term": "Claim Amount",
    "description": "Monetary value of insurance claim"
  }
]
```

### Text Example
```
Premium: The amount paid by the policyholder for insurance coverage.
Examples include monthly premiums of $150 or annual premiums of $1,800.

Claim: A formal request for coverage or compensation for a covered loss.
```

**Note**: The app intelligently extracts information from each line item and enriches missing fields using AI (Flask version) or smart heuristics (HTML version).

## Architecture

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Integration**: Claude API (with fallback to sample data)
- **File Processing**: Pandas for data parsing

## Project Structure

```
Claudecodeapps/
├── business-glossary-generator.html    # Standalone HTML version (no server needed)
├── app.py                              # Flask application and API endpoints
├── templates/
│   └── index.html                      # Flask web interface
├── static/
│   ├── style.css                       # Styling
│   └── script.js                       # Frontend logic
├── sample_data/                        # Example files for testing
│   ├── general_insurance_glossary.csv  # General insurance terms
│   ├── life_insurance_glossary.csv     # Life insurance terms
│   ├── it_glossary.csv                 # IT terms (CSV format)
│   ├── it_glossary.json                # IT terms (JSON format)
│   └── insurance_terms.txt             # Insurance terms (text format)
├── uploads/                            # Temporary file storage (auto-created)
├── requirements.txt                    # Python dependencies
├── README.md                           # Main documentation
├── HTML_VERSION_README.md              # Standalone HTML version docs
└── QUICKSTART.md                       # Quick start guide
```

## Configuration

The application can be configured through environment variables:

- `ANTHROPIC_API_KEY`: Your Claude API key for AI-powered glossary generation
- `FLASK_ENV`: Set to `development` for debug mode (default) or `production`

## Security Notes

- Maximum file upload size: 16MB
- Uploaded files are automatically deleted after processing
- Only specified file formats are accepted
- File paths are sanitized using `secure_filename()`

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT License

## Support

For issues and feature requests, please create an issue in the repository.
