// Global state
let currentColumns = [];
let currentGlossary = [];
let clarifications = {};

// DOM elements
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('file');
const submitBtn = document.getElementById('submitBtn');
const errorMessage = document.getElementById('errorMessage');

const uploadSection = document.getElementById('uploadSection');
const deduplicationSection = document.getElementById('deduplicationSection');
const resultsSection = document.getElementById('resultsSection');

const totalColumnsEl = document.getElementById('totalColumns');
const deduplicatedCountEl = document.getElementById('deduplicatedCount');
const duplicatesRemovedEl = document.getElementById('duplicatesRemoved');

const abbreviationsPanel = document.getElementById('abbreviationsPanel');
const abbreviationsForm = document.getElementById('abbreviationsForm');
const generateBtn = document.getElementById('generateBtn');
const startOverBtn = document.getElementById('startOverBtn');

const glossaryResults = document.getElementById('glossaryResults');
const termCountEl = document.getElementById('termCount');
const downloadBtn = document.getElementById('downloadBtn');
const exportCsvBtn = document.getElementById('exportCsvBtn');
const newGlossaryBtn = document.getElementById('newGlossaryBtn');

// File input visual feedback
fileInput.addEventListener('change', (e) => {
    const fileName = e.target.files[0]?.name || 'Choose a file or drag it here';
    document.querySelector('.file-text').textContent = fileName;
});

// Form submission - Step 1: Upload and analyze
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    showLoading(submitBtn, true);
    hideError();

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            currentColumns = data.columns;
            showDeduplicationResults(data);
        } else {
            showError(data.error || 'Failed to process file');
        }
    } catch (error) {
        showError('An error occurred while uploading the file');
    } finally {
        showLoading(submitBtn, false);
    }
});

// Generate glossary - Step 2
generateBtn.addEventListener('click', async () => {
    // Collect abbreviation clarifications
    clarifications = {};
    const abbreviationSelects = document.querySelectorAll('.abbreviation-select');
    abbreviationSelects.forEach(select => {
        clarifications[select.dataset.abbreviation] = select.value;
    });

    showLoading(generateBtn, true);
    hideError();

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                columns: currentColumns,
                clarifications: clarifications
            })
        });

        const data = await response.json();

        if (data.success) {
            currentGlossary = data.glossary;
            showGlossaryResults(data);
        } else {
            showError(data.error || 'Failed to generate glossary');
        }
    } catch (error) {
        showError('An error occurred while generating the glossary');
    } finally {
        showLoading(generateBtn, false);
    }
});

// Download XLSX
downloadBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                glossary: currentGlossary
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Insurance_Business_Glossary_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            showError('Failed to download XLSX file');
        }
    } catch (error) {
        showError('An error occurred while downloading the file');
    }
});

// Export to CSV
exportCsvBtn.addEventListener('click', () => {
    const csvContent = generateCSV(currentGlossary);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `Insurance_Business_Glossary_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// Start over / New glossary
startOverBtn.addEventListener('click', resetApp);
newGlossaryBtn.addEventListener('click', resetApp);

function showDeduplicationResults(data) {
    // Hide upload section
    uploadSection.style.display = 'none';

    // Show deduplication section
    deduplicationSection.style.display = 'block';

    // Update stats
    totalColumnsEl.textContent = data.total_columns;
    deduplicatedCountEl.textContent = data.deduplicated_count;
    duplicatesRemovedEl.textContent = data.duplicates_removed;

    // Show abbreviations if any
    if (data.abbreviations && data.abbreviations.length > 0) {
        abbreviationsPanel.style.display = 'block';
        renderAbbreviationsForm(data.abbreviations);
    } else {
        abbreviationsPanel.style.display = 'none';
    }
}

function renderAbbreviationsForm(abbreviations) {
    abbreviationsForm.innerHTML = '';

    abbreviations.forEach(abbrev => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';

        const label = document.createElement('label');
        label.textContent = `${abbrev.abbreviation} (found in: ${abbrev.example_columns.join(', ')})`;

        const select = document.createElement('select');
        select.className = 'abbreviation-select';
        select.dataset.abbreviation = abbrev.abbreviation;
        select.required = true;

        // Add placeholder option
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = '-- Select meaning --';
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        select.appendChild(placeholderOption);

        // Add meaning options
        abbrev.possible_meanings.forEach(meaning => {
            const option = document.createElement('option');
            option.value = meaning;
            option.textContent = meaning;
            select.appendChild(option);
        });

        formGroup.appendChild(label);
        formGroup.appendChild(select);
        abbreviationsForm.appendChild(formGroup);
    });
}

function showGlossaryResults(data) {
    // Hide deduplication section
    deduplicationSection.style.display = 'none';

    // Show results section
    resultsSection.style.display = 'block';

    // Update term count
    termCountEl.textContent = data.total_terms;

    // Render glossary as cards with three-layer structure
    renderGlossaryCards(data.glossary);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function renderGlossaryCards(glossary) {
    glossaryResults.innerHTML = '';

    glossary.forEach(item => {
        const card = document.createElement('div');
        card.className = 'glossary-card';

        // Header with term and domain badge
        const header = document.createElement('div');
        header.className = 'card-header';
        header.innerHTML = `
            <h3>${escapeHtml(item.business_term)}</h3>
            <span class="domain-badge">${escapeHtml(item.data_domain)}</span>
        `;
        card.appendChild(header);

        // Layer 1: Business Definition
        const layer1 = document.createElement('div');
        layer1.className = 'layer-section layer-1';
        layer1.innerHTML = `
            <div class="layer-label">Layer 1: Business Definition</div>
            <p class="layer-content">${escapeHtml(item.business_definition)}</p>
        `;
        card.appendChild(layer1);

        // Layer 2: Business Context
        const layer2 = document.createElement('div');
        layer2.className = 'layer-section layer-2';
        layer2.innerHTML = `
            <div class="layer-label">Layer 2: Business Context</div>
            <p class="layer-content">${escapeHtml(item.business_context)}</p>
        `;
        card.appendChild(layer2);

        // Layer 3: Technical Bridge (optional, collapsible)
        if (item.technical_bridge) {
            const layer3 = document.createElement('div');
            layer3.className = 'layer-section layer-3';
            layer3.innerHTML = `
                <div class="layer-label collapsible">
                    <span>Layer 3: Technical Bridge</span>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="layer-content collapsible-content">
                    ${escapeHtml(item.technical_bridge)}
                </div>
            `;

            // Make it collapsible
            const labelEl = layer3.querySelector('.layer-label');
            const contentEl = layer3.querySelector('.layer-content');
            labelEl.addEventListener('click', () => {
                contentEl.classList.toggle('expanded');
                labelEl.querySelector('.toggle-icon').textContent =
                    contentEl.classList.contains('expanded') ? '▲' : '▼';
            });

            card.appendChild(layer3);
        }

        // Additional info section
        const additionalInfo = document.createElement('div');
        additionalInfo.className = 'additional-info';

        let infoHTML = '';

        // Synonyms
        if (item.synonyms && item.synonyms.length > 0) {
            infoHTML += `
                <div class="info-item">
                    <strong>Synonyms:</strong> ${item.synonyms.map(s => `<span class="tag">${escapeHtml(s)}</span>`).join(' ')}
                </div>
            `;
        }

        // Allowed Values
        if (item.allowed_values && item.allowed_values.length > 0) {
            infoHTML += `
                <div class="info-item">
                    <strong>Allowed Values:</strong> ${item.allowed_values.map(v => `<code>${escapeHtml(v)}</code>`).join(', ')}
                </div>
            `;
        }

        // Associated Columns
        if (item.associated_columns) {
            const columns = item.associated_columns.split('|');
            infoHTML += `
                <div class="info-item">
                    <strong>Associated Database Columns:</strong> ${columns.map(c => `<code>${escapeHtml(c)}</code>`).join(', ')}
                </div>
            `;
        }

        if (infoHTML) {
            additionalInfo.innerHTML = infoHTML;
            card.appendChild(additionalInfo);
        }

        glossaryResults.appendChild(card);
    });
}

function generateCSV(glossary) {
    const headers = [
        'Business Term',
        'Business Definition',
        'Business Context',
        'Technical Bridge',
        'Synonyms',
        'Allowed Values',
        'Data Domain',
        'Associated Database Columns'
    ];

    const rows = glossary.map(item => [
        item.business_term || '',
        item.business_definition || '',
        item.business_context || '',
        item.technical_bridge || '',
        (item.synonyms || []).join('; '),
        (item.allowed_values || []).join('; '),
        item.data_domain || '',
        item.associated_columns || ''
    ]);

    const csvRows = [headers, ...rows].map(row =>
        row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    );

    return csvRows.join('\n');
}

function showLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text') || button.querySelector('span');
    const spinner = button.querySelector('.spinner');

    if (isLoading) {
        button.disabled = true;
        if (btnText) btnText.style.display = 'none';
        if (spinner) spinner.style.display = 'inline-block';
    } else {
        button.disabled = false;
        if (btnText) btnText.style.display = 'inline';
        if (spinner) spinner.style.display = 'none';
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
    errorMessage.style.display = 'none';
}

function resetApp() {
    // Reset state
    currentColumns = [];
    currentGlossary = [];
    clarifications = {};

    // Reset form
    uploadForm.reset();
    document.querySelector('.file-text').textContent = 'Choose a file or drag it here';

    // Show upload section
    uploadSection.style.display = 'block';

    // Hide other sections
    deduplicationSection.style.display = 'none';
    resultsSection.style.display = 'none';

    // Clear error
    hideError();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
