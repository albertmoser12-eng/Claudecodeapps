# Quick Start Guide

## Running the Application

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```bash
   python app.py
   ```

3. **Access the Application**
   Open your web browser and go to: `http://localhost:5000`

## Using the Application

### Step 1: Select Business Context
Choose the appropriate business domain from the dropdown:
- **General Insurance**: For property, casualty, and general insurance terms
- **Life Insurance**: For life insurance, annuities, and related products
- **Information Technology**: For software systems, databases, and IT metrics

### Step 2: Upload Your File
Click on the upload area or drag and drop a file. Supported formats:
- CSV (.csv)
- Excel (.xlsx, .xls)
- JSON (.json)
- Text (.txt)

### Step 3: Generate Glossary
Click the "Generate Glossary" button. The application will:
1. Parse your uploaded file
2. Analyze the content using AI
3. Extract business terms and metrics
4. Display results in a comprehensive table

### Step 4: Review and Export
- Review the generated glossary table with all 8 columns
- Click "Export to CSV" to download the results

## Example Files

The `sample_data/` directory contains example files you can use to test:
- `insurance_data.csv` - General insurance fields
- `life_insurance_terms.txt` - Life insurance definitions
- `it_systems.json` - IT system schema

## AI-Powered Generation (Optional)

For enhanced AI-powered glossary generation, set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Without an API key, the application will use pre-configured sample glossaries based on your selected business context.

## Troubleshooting

**Port 5000 already in use?**
Change the port in app.py:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

**File upload fails?**
Check the file size (max 16MB) and format (must be .csv, .xlsx, .xls, .json, or .txt)

**No results generated?**
Ensure your file contains structured data that can be parsed. Check the server logs for errors.

## Column Descriptions

The generated glossary includes these columns:

1. **Title**: Name of the business term or metric
2. **Description**: Clear explanation of the concept
3. **Examples**: Real-world usage examples
4. **Business Logic**: Rules and logic governing the term
5. **Data Type**: Technical data type (string, number, date, etc.)
6. **Technical Aliases**: Alternative technical names or database columns
7. **Synonyms**: Other business terms with similar meaning
8. **Logical Formula**: Calculation formula (for metrics only)
