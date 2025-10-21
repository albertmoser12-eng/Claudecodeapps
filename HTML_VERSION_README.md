# Standalone HTML Version - Business Glossary Generator

This is a **standalone, single-file HTML version** of the Business Glossary Generator that runs entirely in your web browser with **no server or backend required**.

## Features

- **Zero Installation**: Just open the HTML file in any modern web browser
- **Client-Side Processing**: All file parsing and glossary generation happens locally
- **Privacy Focused**: Your files never leave your computer
- **Fully Self-Contained**: All CSS and JavaScript embedded in one file
- **Portable**: Copy the file anywhere and it works

## How to Use

### Option 1: Double-Click
Simply double-click `business-glossary-generator.html` to open it in your default browser.

### Option 2: Open in Browser
1. Open your web browser (Chrome, Firefox, Safari, Edge)
2. Press `Ctrl+O` (or `Cmd+O` on Mac) to open a file
3. Navigate to and select `business-glossary-generator.html`

### Option 3: Host on Web Server
You can also host this file on any web server or upload it to a static hosting service.

## Using the Application

1. **Select Business Context**
   - General Insurance
   - Life Insurance
   - Information Technology

2. **Upload Your File**
   - Supported formats: CSV, JSON, TXT
   - Drag and drop or click to browse
   - Note: Excel files require the full Flask backend version

3. **Generate Glossary**
   - Click "Generate Glossary"
   - The app will parse your file and extract business terms
   - View results in the comprehensive 8-column table

4. **Export Results**
   - Click "Export to CSV" to download your glossary

## Supported File Formats

### CSV Files
The app will extract column headers and generate glossary entries for each field.

Example:
```csv
policy_number,premium_amount,coverage_limit
POL-001,1500.00,500000
```

### JSON Files
The app will traverse the JSON structure and extract field definitions.

Example:
```json
{
  "user_id": {
    "description": "Unique user identifier",
    "type": "VARCHAR(50)",
    "example": "USR-123"
  }
}
```

### Text Files
The app will look for term definitions in the format:
```
Term Name: Description of the term
Another Term - Description here
```

## How It Works

The standalone version uses intelligent client-side parsing:

1. **File Parsing**: JavaScript FileReader API reads the uploaded file
2. **Format Detection**: Automatically detects CSV, JSON, or TXT format
3. **Term Extraction**: Parses content to identify business terms
4. **Smart Generation**: Uses heuristics to generate:
   - Descriptions based on field names
   - Data type inference
   - Technical aliases (snake_case, camelCase, etc.)
   - Business logic based on field type
   - Formulas for metric fields
5. **Fallback Templates**: If extraction yields minimal results, uses pre-configured glossaries

## Output Columns

1. **Title**: Name of the business term or metric
2. **Description**: Clear explanation of the concept
3. **Examples**: Sample values or use cases
4. **Business Logic**: Rules governing the term
5. **Data Type**: Technical data type classification
6. **Technical Aliases**: Alternative names (database columns, API fields)
7. **Synonyms**: Business synonyms
8. **Logical Formula**: Calculation formula (for metrics)

## Differences from Flask Version

| Feature | Standalone HTML | Flask Backend |
|---------|----------------|---------------|
| Installation | None | Python + packages |
| Server Required | No | Yes |
| Excel Support | No | Yes |
| AI Generation | Template-based | Claude API (optional) |
| File Processing | Client-side | Server-side |
| Deployment | Copy single file | Deploy app |
| Privacy | 100% local | Files uploaded to server |

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## File Size

The standalone HTML file is approximately 36 KB - small enough to email or share easily.

## Security

- All processing happens in your browser
- No data is sent to any server
- No external dependencies or CDNs
- No cookies or tracking

## Customization

You can customize the glossary templates by editing the `glossaryTemplates` object in the `<script>` section of the HTML file.

## Troubleshooting

**File won't upload?**
- Check file format (must be .csv, .json, or .txt)
- File size limit is determined by browser memory (typically several MB is fine)

**Results look generic?**
- The standalone version uses intelligent heuristics but may not be as detailed as the AI-powered Flask version
- Try formatting your input file with clear field names and descriptions

**Not working in browser?**
- Ensure JavaScript is enabled
- Try a different modern browser
- Check browser console (F12) for error messages

## When to Use Each Version

**Use the Standalone HTML Version when:**
- You want quick, offline analysis
- You don't want to install Python/Flask
- You need maximum privacy (local processing)
- You're working with CSV, JSON, or TXT files
- You want to share the tool easily (just email the HTML file)

**Use the Flask Backend Version when:**
- You need Excel file support
- You want AI-powered analysis with Claude API
- You're deploying for a team/organization
- You need more advanced customization
- You want to integrate with other systems

## License

MIT License - Same as the main project
