# Business Glossary Generator

A web application that automatically generates comprehensive business glossaries from uploaded data files. The app uses AI to parse documents and extract business terms, metrics, and their detailed attributes.

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

## File Format Examples

### CSV Example
```csv
Field Name,Description,Sample Value
policy_number,Unique identifier for insurance policy,POL-2024-001
premium_amount,Annual premium payment,1500.00
coverage_limit,Maximum claim amount,500000.00
```

### JSON Example
```json
{
  "fields": [
    {"name": "customer_id", "description": "Unique customer identifier"},
    {"name": "claim_amount", "description": "Total claim value in USD"}
  ]
}
```

## Architecture

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Integration**: Claude API (with fallback to sample data)
- **File Processing**: Pandas for data parsing

## Project Structure

```
Claudecodeapps/
├── app.py                 # Flask application and API endpoints
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend logic
├── uploads/              # Temporary file storage (auto-created)
├── requirements.txt      # Python dependencies
└── README.md            # Documentation
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
