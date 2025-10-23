#!/usr/bin/env python3
"""
Generate Azure Deployment Requirements documentation in .docx format
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

def add_heading(doc, text, level=1):
    """Add a heading with custom formatting"""
    heading = doc.add_heading(text, level=level)
    heading.paragraph_format.space_before = Pt(12)
    heading.paragraph_format.space_after = Pt(6)
    return heading

def add_code_block(doc, code_text):
    """Add a code block with monospace formatting"""
    p = doc.add_paragraph()
    p.style = 'Normal'
    run = p.add_run(code_text)
    run.font.name = 'Courier New'
    run.font.size = Pt(9)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    # Add light gray background effect
    return p

def create_azure_requirements_doc():
    """Create the complete Azure requirements document"""
    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    # Title page
    title = doc.add_heading('Microsoft Azure Deployment Requirements', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.add_paragraph('Business Glossary Generator')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].font.size = Pt(16)
    subtitle.runs[0].font.color.rgb = RGBColor(68, 114, 196)

    doc.add_paragraph()  # Spacing

    # Document info
    info = doc.add_paragraph()
    info.add_run('Document Version: ').bold = True
    info.add_run('1.0\n')
    info.add_run('Date: ').bold = True
    info.add_run('October 2025\n')
    info.add_run('Application: ').bold = True
    info.add_run('Business Glossary Generator (Flask + Claude API)')
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # ========== APPLICATION OVERVIEW ==========
    add_heading(doc, '1. Application Overview', level=1)

    doc.add_paragraph(
        'The Business Glossary Generator is a Flask web application that creates '
        'comprehensive business glossaries with three-layer definition structures.'
    )

    add_heading(doc, 'Technology Stack', level=2)
    components = [
        'Backend: Flask (Python 3.9+)',
        'Frontend: HTML/CSS/JavaScript (served by Flask)',
        'API Integration: Anthropic Claude API (claude-3-5-sonnet-20241022)',
        'File Processing: pandas, openpyxl',
        'Storage: Temporary file storage for uploads/outputs',
        'Max File Size: 16 MB per upload'
    ]
    for component in components:
        doc.add_paragraph(component, style='List Bullet')

    doc.add_page_break()

    # ========== AZURE SERVICE OPTIONS ==========
    add_heading(doc, '2. Azure Service Options', level=1)

    # Option 1: App Service
    add_heading(doc, 'Option 1: Azure App Service (Recommended)', level=2)

    doc.add_paragraph(
        'Azure App Service is the recommended deployment option for this Flask application. '
        'It provides a fully managed platform with built-in scaling, monitoring, and deployment options.'
    )

    add_heading(doc, 'Service Requirements', level=3)
    requirements = [
        'Service: Azure App Service (Web App)',
        'Runtime: Python 3.9 or higher',
        'OS: Linux (recommended for Python)',
        'Pricing Tier: Minimum B1 (Basic) or higher'
    ]
    for req in requirements:
        doc.add_paragraph(req, style='List Bullet')

    add_heading(doc, 'Technical Specifications', level=3)

    doc.add_paragraph('Minimum Requirements (Development/Testing):').runs[0].bold = True
    min_specs = [
        'Tier: B1 Basic',
        'vCPU: 1 core',
        'RAM: 1.75 GB',
        'Storage: 10 GB',
        'Cost: ~$13-15/month'
    ]
    for spec in min_specs:
        doc.add_paragraph(spec, style='List Bullet 2')

    doc.add_paragraph('Recommended for Production:').runs[0].bold = True
    prod_specs = [
        'Tier: S1 Standard or P1V2 Premium',
        'vCPU: 1-2 cores',
        'RAM: 3.5 GB',
        'Storage: 50 GB',
        'Features: Auto-scaling, custom domains, SSL certificates',
        'Cost: $70-100/month (S1) or $85-120/month (P1V2)'
    ]
    for spec in prod_specs:
        doc.add_paragraph(spec, style='List Bullet 2')

    add_heading(doc, 'Configuration Requirements', level=3)

    doc.add_paragraph('Application Settings (Environment Variables):').runs[0].bold = True
    add_code_block(doc, '''ANTHROPIC_API_KEY=<your-api-key>
SCM_DO_BUILD_DURING_DEPLOYMENT=true
WEBSITES_ENABLE_APP_SERVICE_STORAGE=false''')

    doc.add_paragraph('Startup Command:').runs[0].bold = True
    add_code_block(doc, 'gunicorn --bind 0.0.0.0:8000 --timeout 120 app:app')

    doc.add_paragraph('Python Requirements (requirements.txt):').runs[0].bold = True
    add_code_block(doc, '''Flask==3.0.0
pandas==2.1.0
openpyxl==3.1.2
anthropic==0.7.0
werkzeug==3.0.0
gunicorn==21.2.0''')

    doc.add_page_break()

    # Option 2: Container Instances
    add_heading(doc, 'Option 2: Azure Container Instances (ACI)', level=2)

    doc.add_paragraph(
        'Azure Container Instances provides a lightweight containerized deployment option '
        'suitable for isolated workloads without orchestration overhead.'
    )

    add_heading(doc, 'Service Requirements', level=3)
    aci_reqs = [
        'Service: Azure Container Instances',
        'Container: Custom Docker image',
        'Registry: Azure Container Registry (ACR)',
        'CPU: 1 vCPU',
        'Memory: 2 GB',
        'Storage: 10 GB (for temp files)',
        'Port: 5000 or 8000',
        'Cost: ~$30-50/month'
    ]
    for req in aci_reqs:
        doc.add_paragraph(req, style='List Bullet')

    add_heading(doc, 'Dockerfile Example', level=3)
    add_code_block(doc, '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV ANTHROPIC_API_KEY=""

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]''')

    doc.add_page_break()

    # Option 3: AKS
    add_heading(doc, 'Option 3: Azure Kubernetes Service (AKS)', level=2)

    doc.add_paragraph(
        'AKS is recommended for enterprise deployments requiring high availability, '
        'advanced orchestration, and multi-service architectures.'
    )

    add_heading(doc, 'Cluster Requirements', level=3)
    aks_reqs = [
        'Service: Azure Kubernetes Service',
        'Node Pool: 2-3 nodes minimum',
        'Node VM Size: Standard_B2s or higher',
        'Node Count: 2-3 nodes',
        'Total vCPU: 4-6 cores',
        'Total Memory: 8-12 GB',
        'Container Registry: Azure Container Registry',
        'Cost: ~$150-300/month'
    ]
    for req in aks_reqs:
        doc.add_paragraph(req, style='List Bullet')

    doc.add_paragraph().add_run('Best For:').bold = True
    best_for = [
        'High availability requirements',
        'Auto-scaling needs',
        'Multi-service deployments',
        'Enterprise-grade deployments'
    ]
    for item in best_for:
        doc.add_paragraph(item, style='List Bullet 2')

    doc.add_page_break()

    # ========== STORAGE REQUIREMENTS ==========
    add_heading(doc, '3. Storage Requirements', level=1)

    add_heading(doc, 'Temporary Storage', level=2)
    doc.add_paragraph(
        'The application creates temporary directories for file uploads and outputs:'
    )
    storage_dirs = [
        'uploads/ - Stores uploaded files temporarily',
        'outputs/ - Stores generated XLSX files temporarily'
    ]
    for dir_info in storage_dirs:
        doc.add_paragraph(dir_info, style='List Bullet')

    add_heading(doc, 'Azure Storage Options', level=3)
    options = [
        'App Service File System (included, ephemeral) - No additional cost',
        'Azure Blob Storage (persistent, recommended for production)',
    ]
    for option in options:
        doc.add_paragraph(option, style='List Bullet')

    blob_details = [
        'Container for uploads: ~1 GB',
        'Container for outputs: ~5 GB',
        'Cost: ~$0.02-0.05/GB/month'
    ]
    for detail in blob_details:
        doc.add_paragraph(detail, style='List Bullet 2')

    add_heading(doc, 'Persistent Storage Configuration', level=3)
    doc.add_paragraph('If using Azure Blob Storage, the following resources are required:')
    blob_reqs = [
        'Storage Account (Standard LRS)',
        'Blob Container for uploads',
        'Blob Container for outputs'
    ]
    for req in blob_reqs:
        doc.add_paragraph(req, style='List Bullet')

    doc.add_paragraph('Additional Python Package Required:').runs[0].bold = True
    add_code_block(doc, 'azure-storage-blob==12.19.0')

    doc.add_paragraph('Code Modifications:').runs[0].bold = True
    add_code_block(doc, '''from azure.storage.blob import BlobServiceClient

# Replace file system operations with blob storage
blob_service_client = BlobServiceClient.from_connection_string(
    os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
)''')

    doc.add_page_break()

    # ========== NETWORK & SECURITY ==========
    add_heading(doc, '4. Network & Security Requirements', level=1)

    add_heading(doc, 'Networking', level=2)
    network_reqs = [
        'Inbound Ports: 80 (HTTP), 443 (HTTPS)',
        'Outbound Access: Required to Anthropic API (api.anthropic.com)',
        'Virtual Network: Optional (for enhanced security)',
        'Private Endpoints: Optional (for enterprise deployments)'
    ]
    for req in network_reqs:
        doc.add_paragraph(req, style='List Bullet')

    add_heading(doc, 'Security Requirements', level=2)

    doc.add_paragraph('SSL/TLS Certificate:').runs[0].bold = True
    ssl_options = [
        'Free via Azure App Service Managed Certificate',
        'Custom certificate via Azure Key Vault'
    ]
    for option in ssl_options:
        doc.add_paragraph(option, style='List Bullet')

    doc.add_paragraph('Authentication Options:').runs[0].bold = True
    auth_options = [
        'Azure AD Integration (recommended for enterprise)',
        'Basic Authentication (via Flask)',
        'IP Restrictions (whitelist specific IPs)'
    ]
    for option in auth_options:
        doc.add_paragraph(option, style='List Bullet')

    add_heading(doc, 'Secrets Management', level=3)
    doc.add_paragraph(
        'Azure Key Vault (Recommended): Store sensitive configuration like ANTHROPIC_API_KEY'
    )
    kv_details = [
        'Cost: ~$0.03 per 10,000 operations',
        'Estimated Monthly Cost: ~$3-5',
        'Benefits: Centralized secrets management, audit logging, RBAC'
    ]
    for detail in kv_details:
        doc.add_paragraph(detail, style='List Bullet')

    doc.add_paragraph('Key Vault Integration Code:').runs[0].bold = True
    add_code_block(doc, '''from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://<vault-name>.vault.azure.net/",
    credential=credential
)
api_key = client.get_secret("anthropic-api-key").value''')

    doc.add_page_break()

    # ========== API REQUIREMENTS ==========
    add_heading(doc, '5. API Requirements', level=1)

    add_heading(doc, 'Anthropic Claude API', level=2)
    api_reqs = [
        'API Key: Required (stored as environment variable or Key Vault)',
        'Model: claude-3-5-sonnet-20241022',
        'Rate Limits: Depends on your Anthropic subscription plan',
        'Network Access: Outbound HTTPS to api.anthropic.com',
        'Timeout: 120 seconds configured for API calls'
    ]
    for req in api_reqs:
        doc.add_paragraph(req, style='List Bullet')

    add_heading(doc, 'Anthropic API Pricing (Separate from Azure)', level=3)
    doc.add_paragraph('Claude 3.5 Sonnet Pricing:')
    pricing = [
        'Input: $3 per million tokens',
        'Output: $15 per million tokens',
        'Estimated monthly cost depends on usage volume'
    ]
    for price in pricing:
        doc.add_paragraph(price, style='List Bullet')

    doc.add_page_break()

    # ========== PERFORMANCE & SCALING ==========
    add_heading(doc, '6. Performance & Scaling', level=1)

    add_heading(doc, 'Performance Considerations', level=2)
    perf_specs = [
        'Max Request Size: 16 MB (configured in app.py)',
        'Request Timeout: 120 seconds (for Claude API calls)',
        'Concurrent Users: 10-50 (depending on tier)',
        'File Processing: CSV, JSON, TXT, Excel (XLSX/XLS)'
    ]
    for spec in perf_specs:
        doc.add_paragraph(spec, style='List Bullet')

    add_heading(doc, 'Vertical Scaling (Scale Up)', level=3)
    doc.add_paragraph('Increase resources of a single instance:')
    scale_up = [
        'B1 → S1: More CPU/memory for production workloads',
        'S1 → P1V2: Premium performance with enhanced features',
        'P1V2 → P2V2/P3V2: High-performance production'
    ]
    for option in scale_up:
        doc.add_paragraph(option, style='List Bullet')

    add_heading(doc, 'Horizontal Scaling (Scale Out)', level=3)
    doc.add_paragraph('Add multiple instances for load distribution:')
    scale_out = [
        'Instance Count: Min 1, Max 10+ (depending on tier)',
        'Auto-scale based on metrics (CPU, Memory, Request Queue)',
        'Load balancing automatically configured'
    ]
    for option in scale_out:
        doc.add_paragraph(option, style='List Bullet')

    add_heading(doc, 'Auto-Scale Configuration Example', level=3)
    doc.add_paragraph('Scale out when:')
    rules = [
        'CPU percentage > 70% for 5 minutes',
        'Memory percentage > 80% for 5 minutes',
        'Request queue length > 100 requests'
    ]
    for rule in rules:
        doc.add_paragraph(rule, style='List Bullet')

    doc.add_page_break()

    # ========== MONITORING ==========
    add_heading(doc, '7. Monitoring & Diagnostics', level=1)

    add_heading(doc, 'Application Insights', level=2)
    doc.add_paragraph(
        'Azure Application Insights provides comprehensive monitoring and diagnostics.'
    )

    doc.add_paragraph('Features:').runs[0].bold = True
    features = [
        'Request tracking and response times',
        'Dependency tracking (Claude API calls)',
        'Exception logging and stack traces',
        'Performance metrics and bottleneck identification',
        'Custom metrics and events',
        'Real-time monitoring dashboard'
    ]
    for feature in features:
        doc.add_paragraph(feature, style='List Bullet')

    doc.add_paragraph('Cost: ~$2-10/GB of data ingested (first 5GB/month free)')

    add_heading(doc, 'Python Integration', level=3)
    doc.add_paragraph('Required packages:').runs[0].bold = True
    add_code_block(doc, '''opencensus-ext-azure==1.1.9
opencensus-ext-flask==0.8.1''')

    doc.add_paragraph('Integration code:').runs[0].bold = True
    add_code_block(doc, '''from opencensus.ext.azure import metrics_exporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware

middleware = FlaskMiddleware(
    app,
    exporter=metrics_exporter.MetricsExporter(
        connection_string=os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
    )
)''')

    add_heading(doc, 'Logging Options', level=2)
    logging_options = [
        'App Service Logs: Included, accessible via Azure Portal',
        'Log Stream: Real-time log viewing',
        'Log Analytics: Advanced querying and analysis (~$2-5/GB)',
        'Diagnostic Settings: Export logs to Storage Account or Event Hub'
    ]
    for option in logging_options:
        doc.add_paragraph(option, style='List Bullet')

    doc.add_page_break()

    # ========== COST ESTIMATES ==========
    add_heading(doc, '8. Cost Estimate Summary', level=1)

    add_heading(doc, 'Minimum Production Setup (~$18/month)', level=2)

    # Create table for minimum setup
    table = doc.add_table(rows=7, cols=4)
    table.style = 'Light Grid Accent 1'

    # Header row
    header_cells = table.rows[0].cells
    headers = ['Component', 'Service', 'Specification', 'Monthly Cost']
    for i, header in enumerate(headers):
        header_cells[i].text = header
        header_cells[i].paragraphs[0].runs[0].bold = True

    # Data rows
    data = [
        ['Compute', 'App Service B1', '1 vCPU, 1.75GB RAM', '$13'],
        ['Storage', 'App Service (included)', '10 GB', '$0'],
        ['Monitoring', 'Application Insights', '1 GB data', '$2'],
        ['Secrets', 'Key Vault', 'Standard', '$3'],
        ['SSL', 'Managed Certificate', 'Free', '$0'],
        ['Total Azure', '', '', '~$18/month']
    ]

    for i, row_data in enumerate(data, start=1):
        cells = table.rows[i].cells
        for j, cell_text in enumerate(row_data):
            cells[j].text = cell_text
            if 'Total' in cell_text:
                cells[j].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_paragraph('Note: Anthropic API costs are separate and usage-based.')

    doc.add_page_break()

    add_heading(doc, 'Recommended Production Setup (~$85/month)', level=2)

    # Create table for recommended setup
    table = doc.add_table(rows=8, cols=4)
    table.style = 'Light Grid Accent 1'

    # Header row
    header_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        header_cells[i].text = header
        header_cells[i].paragraphs[0].runs[0].bold = True

    # Data rows
    data = [
        ['Compute', 'App Service S1', '1 vCPU, 3.5GB RAM', '$70'],
        ['Storage', 'Blob Storage', '10 GB', '$0.50'],
        ['Monitoring', 'Application Insights', '5 GB data', '$10'],
        ['Secrets', 'Key Vault', 'Standard', '$3'],
        ['SSL', 'Managed Certificate', 'Free', '$0'],
        ['Backup', 'Blob Snapshots', 'Daily', '$2'],
        ['Total Azure', '', '', '~$85/month']
    ]

    for i, row_data in enumerate(data, start=1):
        cells = table.rows[i].cells
        for j, cell_text in enumerate(row_data):
            cells[j].text = cell_text
            if 'Total' in cell_text:
                cells[j].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_paragraph('Note: Anthropic API costs are separate and usage-based.')

    doc.add_page_break()

    add_heading(doc, 'Enterprise Setup (~$265/month)', level=2)

    # Create table for enterprise setup
    table = doc.add_table(rows=7, cols=4)
    table.style = 'Light Grid Accent 1'

    # Header row
    header_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        header_cells[i].text = header
        header_cells[i].paragraphs[0].runs[0].bold = True

    # Data rows
    data = [
        ['Compute', 'App Service P1V2 + Scale', '2+ instances', '$200'],
        ['Storage', 'Blob Storage Premium', '50 GB', '$5'],
        ['Networking', 'Virtual Network', 'Standard', '$5'],
        ['Monitoring', 'App Insights + Log Analytics', '20 GB', '$40'],
        ['Security', 'Key Vault + Private Link', 'Premium', '$15'],
        ['Total Azure', '', '', '~$265/month']
    ]

    for i, row_data in enumerate(data, start=1):
        cells = table.rows[i].cells
        for j, cell_text in enumerate(row_data):
            cells[j].text = cell_text
            if 'Total' in cell_text:
                cells[j].paragraphs[0].runs[0].bold = True

    doc.add_paragraph()
    doc.add_paragraph('Note: Anthropic API costs are separate and usage-based.')

    doc.add_page_break()

    # ========== DEPLOYMENT METHODS ==========
    add_heading(doc, '9. Deployment Methods', level=1)

    add_heading(doc, 'Method 1: Azure Portal (GUI)', level=2)
    doc.add_paragraph('Step-by-step deployment via web interface:')
    steps = [
        'Create Web App resource in Azure Portal',
        'Configure runtime stack (Python 3.11)',
        'Set environment variables in Configuration',
        'Choose deployment method: GitHub Actions, Azure DevOps, Local Git, or FTP',
        'Deploy application code',
        'Configure custom domain and SSL (optional)'
    ]
    for i, step in enumerate(steps, 1):
        doc.add_paragraph(f'{i}. {step}', style='List Number')

    add_heading(doc, 'Method 2: Azure CLI', level=2)
    doc.add_paragraph('Command-line deployment for automation:')

    add_code_block(doc, '''# Create resource group
az group create --name rg-glossary --location eastus

# Create App Service plan
az appservice plan create \\
  --name plan-glossary \\
  --resource-group rg-glossary \\
  --sku B1 \\
  --is-linux

# Create web app
az webapp create \\
  --name app-glossary-generator \\
  --resource-group rg-glossary \\
  --plan plan-glossary \\
  --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set \\
  --name app-glossary-generator \\
  --resource-group rg-glossary \\
  --settings ANTHROPIC_API_KEY="<your-key>"

# Deploy from local git
az webapp deployment source config-local-git \\
  --name app-glossary-generator \\
  --resource-group rg-glossary''')

    add_heading(doc, 'Method 3: GitHub Actions (CI/CD)', level=2)
    doc.add_paragraph('Automated deployment pipeline:')

    doc.add_paragraph('Create .github/workflows/azure-deploy.yml:').runs[0].bold = True
    add_code_block(doc, '''name: Deploy to Azure App Service

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'app-glossary-generator'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}''')

    doc.add_page_break()

    # ========== PRE-DEPLOYMENT CHECKLIST ==========
    add_heading(doc, '10. Pre-Deployment Checklist', level=1)

    add_heading(doc, 'Azure Resources', level=2)
    azure_checklist = [
        'Azure subscription with appropriate permissions',
        'Resource group created',
        'App Service or ACI created',
        'Storage account (if using persistent storage)',
        'Key Vault (for secrets management)',
        'Application Insights (for monitoring)'
    ]
    for item in azure_checklist:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run('☐ ').font.size = Pt(14)
        p.add_run(item)

    add_heading(doc, 'Application Configuration', level=2)
    app_checklist = [
        'requirements.txt includes all dependencies',
        'Environment variables configured',
        'ANTHROPIC_API_KEY stored securely',
        'Startup command configured',
        'CORS settings configured (if needed)',
        'Max file upload size configured (16MB)'
    ]
    for item in app_checklist:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run('☐ ').font.size = Pt(14)
        p.add_run(item)

    add_heading(doc, 'Security', level=2)
    security_checklist = [
        'SSL/TLS certificate configured',
        'Authentication enabled (if required)',
        'IP restrictions configured (if required)',
        'Secrets moved to Key Vault',
        'Managed identity enabled',
        'Network security groups configured (if using VNet)'
    ]
    for item in security_checklist:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run('☐ ').font.size = Pt(14)
        p.add_run(item)

    add_heading(doc, 'Monitoring', level=2)
    monitoring_checklist = [
        'Application Insights connected',
        'Alerts configured (CPU, Memory, Response Time)',
        'Log retention policy set',
        'Dashboard created',
        'Availability tests configured'
    ]
    for item in monitoring_checklist:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run('☐ ').font.size = Pt(14)
        p.add_run(item)

    doc.add_page_break()

    # ========== ADDITIONAL CONSIDERATIONS ==========
    add_heading(doc, '11. Additional Considerations', level=1)

    add_heading(doc, 'Compliance & Governance', level=2)
    considerations = [
        'Data Residency: Choose appropriate Azure region based on data location requirements',
        'GDPR: If processing EU citizen data, use EU Azure regions',
        'HIPAA: Use HIPAA-compliant Azure services if handling healthcare data',
        'SOC 2: Available with Azure compliance features and audit logs'
    ]
    for consideration in considerations:
        doc.add_paragraph(consideration, style='List Bullet')

    add_heading(doc, 'Disaster Recovery', level=2)
    dr_items = [
        'Backup Strategy: Configure daily blob storage snapshots',
        'Geo-Redundancy: Enable geo-redundant storage (GRS) for critical data',
        'Multi-Region Deployment: Deploy to multiple regions for high availability',
        'Recovery Time Objective (RTO): Plan for acceptable downtime',
        'Recovery Point Objective (RPO): Define acceptable data loss window'
    ]
    for item in dr_items:
        doc.add_paragraph(item, style='List Bullet')

    add_heading(doc, 'Integration Options', level=2)
    integrations = [
        'Azure AD: Single sign-on integration for enterprise users',
        'API Management: Rate limiting, throttling, and API gateway features',
        'Azure Front Door: Global load balancing and CDN capabilities',
        'Logic Apps: Workflow automation and integration with other services',
        'Event Grid: Event-driven architecture integration'
    ]
    for integration in integrations:
        doc.add_paragraph(integration, style='List Bullet')

    doc.add_page_break()

    # ========== QUICK START ==========
    add_heading(doc, '12. Quick Start Guide', level=1)

    doc.add_paragraph(
        'Follow these steps to deploy the Business Glossary Generator to Azure App Service:'
    )

    add_heading(doc, 'Prerequisites', level=2)
    prereqs = [
        'Azure CLI installed (https://aka.ms/installazurecli)',
        'Azure subscription with Owner or Contributor role',
        'Anthropic API key',
        'Application code in a Git repository'
    ]
    for i, prereq in enumerate(prereqs, 1):
        doc.add_paragraph(f'{i}. {prereq}', style='List Number')

    add_heading(doc, 'Deployment Steps', level=2)

    doc.add_paragraph('1. Create Azure Resources').runs[0].bold = True
    add_code_block(doc, '''az group create --name rg-glossary --location eastus
az appservice plan create --name plan-glossary --resource-group rg-glossary --sku B1 --is-linux
az webapp create --name app-glossary-generator --resource-group rg-glossary --plan plan-glossary --runtime "PYTHON:3.11"''')

    doc.add_paragraph('2. Configure Application Settings').runs[0].bold = True
    add_code_block(doc, '''az webapp config appsettings set --name app-glossary-generator --resource-group rg-glossary --settings ANTHROPIC_API_KEY="<your-key>"''')

    doc.add_paragraph('3. Deploy Application Code').runs[0].bold = True
    add_code_block(doc, '''git remote add azure <azure-git-url>
git push azure main:master''')

    doc.add_paragraph('4. Open Application in Browser').runs[0].bold = True
    add_code_block(doc, '''az webapp browse --name app-glossary-generator --resource-group rg-glossary''')

    doc.add_paragraph('5. Verify Deployment').runs[0].bold = True
    verify_steps = [
        'Check application logs in Azure Portal',
        'Test file upload functionality',
        'Verify glossary generation with Claude API',
        'Test XLSX download functionality'
    ]
    for step in verify_steps:
        doc.add_paragraph(step, style='List Bullet')

    doc.add_page_break()

    # ========== TROUBLESHOOTING ==========
    add_heading(doc, '13. Troubleshooting', level=1)

    add_heading(doc, 'Common Issues and Solutions', level=2)

    doc.add_paragraph('Issue: Application fails to start').runs[0].bold = True
    solutions = [
        'Check application logs in Azure Portal → App Service → Log stream',
        'Verify all dependencies are listed in requirements.txt',
        'Ensure Python version matches runtime configuration',
        'Check startup command is correctly configured'
    ]
    for solution in solutions:
        doc.add_paragraph(solution, style='List Bullet')

    doc.add_paragraph()
    doc.add_paragraph('Issue: Claude API timeout errors').runs[0].bold = True
    solutions = [
        'Increase timeout in app configuration (currently 120 seconds)',
        'Check outbound connectivity to api.anthropic.com',
        'Verify ANTHROPIC_API_KEY is correctly configured',
        'Check Anthropic API rate limits and quota'
    ]
    for solution in solutions:
        doc.add_paragraph(solution, style='List Bullet')

    doc.add_paragraph()
    doc.add_paragraph('Issue: File upload failures').runs[0].bold = True
    solutions = [
        'Verify file size is under 16MB limit',
        'Check file format is supported (CSV, JSON, TXT, XLSX)',
        'Ensure sufficient disk space in App Service',
        'Check application logs for specific error messages'
    ]
    for solution in solutions:
        doc.add_paragraph(solution, style='List Bullet')

    doc.add_paragraph()
    doc.add_paragraph('Issue: High memory usage').runs[0].bold = True
    solutions = [
        'Scale up to higher tier with more memory',
        'Monitor Application Insights for memory leaks',
        'Optimize pandas dataframe operations',
        'Implement file size limits for uploads'
    ]
    for solution in solutions:
        doc.add_paragraph(solution, style='List Bullet')

    doc.add_page_break()

    # ========== SUPPORT & RESOURCES ==========
    add_heading(doc, '14. Support & Resources', level=1)

    add_heading(doc, 'Azure Documentation', level=2)
    resources = [
        'Azure App Service: https://docs.microsoft.com/azure/app-service/',
        'Azure CLI Reference: https://docs.microsoft.com/cli/azure/',
        'Python on Azure: https://docs.microsoft.com/azure/developer/python/',
        'Application Insights: https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview'
    ]
    for resource in resources:
        doc.add_paragraph(resource, style='List Bullet')

    add_heading(doc, 'Anthropic API Documentation', level=2)
    doc.add_paragraph('Anthropic API Docs: https://docs.anthropic.com/', style='List Bullet')
    doc.add_paragraph('Claude Models: https://docs.anthropic.com/claude/docs/models-overview', style='List Bullet')

    add_heading(doc, 'Application Repository', level=2)
    doc.add_paragraph('GitHub Repository: https://github.com/albertmoser12-eng/Claudecodeapps', style='List Bullet')

    add_heading(doc, 'Azure Support', level=2)
    support = [
        'Azure Portal Support: Create support ticket in Azure Portal',
        'Azure Community: https://techcommunity.microsoft.com/t5/azure/ct-p/Azure',
        'Stack Overflow: Tag questions with [azure] and [azure-app-service]'
    ]
    for item in support:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_page_break()

    # ========== APPENDIX ==========
    add_heading(doc, 'Appendix A: Required Files Checklist', level=1)

    add_heading(doc, 'Application Files', level=2)
    files = [
        'app.py - Main Flask application',
        'requirements.txt - Python dependencies',
        'templates/index.html - Web interface',
        'static/script.js - Frontend JavaScript',
        'static/style.css - Styling',
        'business-glossary-generator.html - Standalone version (optional)',
        'glossary_instructions.md - Three-layer definition guidelines'
    ]
    for file in files:
        doc.add_paragraph(file, style='List Bullet')

    add_heading(doc, 'Azure Configuration Files (Optional)', level=2)
    config_files = [
        '.github/workflows/azure-deploy.yml - GitHub Actions CI/CD',
        'Dockerfile - Container deployment',
        '.dockerignore - Docker build exclusions',
        'azure-pipelines.yml - Azure DevOps pipeline'
    ]
    for file in config_files:
        doc.add_paragraph(file, style='List Bullet')

    doc.add_page_break()

    # Footer
    footer_section = doc.sections[0]
    footer = footer_section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = "Business Glossary Generator - Azure Deployment Requirements | Page "
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Save document
    output_path = '/home/user/Claudecodeapps/Azure_Deployment_Requirements.docx'
    doc.save(output_path)
    print(f"Document saved to: {output_path}")
    return output_path

if __name__ == '__main__':
    create_azure_requirements_doc()
