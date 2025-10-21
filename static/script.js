document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    const fileLabel = document.querySelector('.file-text');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');
    const errorMessage = document.getElementById('errorMessage');
    const resultsSection = document.getElementById('resultsSection');
    const glossaryBody = document.getElementById('glossaryBody');
    const exportBtn = document.getElementById('exportBtn');

    let currentGlossaryData = [];

    // Update file label when file is selected
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            fileLabel.textContent = e.target.files[0].name;
        } else {
            fileLabel.textContent = 'Choose a file or drag it here';
        }
    });

    // Handle form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Reset UI
        errorMessage.style.display = 'none';
        resultsSection.style.display = 'none';

        // Show loading state
        submitBtn.disabled = true;
        btnText.textContent = 'Processing...';
        spinner.style.display = 'inline-block';

        const formData = new FormData(uploadForm);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                currentGlossaryData = data.glossary;
                displayGlossary(data.glossary);
                resultsSection.style.display = 'block';

                // Scroll to results
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                showError(data.error || 'An error occurred while processing the file');
            }
        } catch (error) {
            showError('Failed to connect to the server. Please try again.');
            console.error('Error:', error);
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            btnText.textContent = 'Generate Glossary';
            spinner.style.display = 'none';
        }
    });

    // Display glossary in table
    function displayGlossary(glossary) {
        glossaryBody.innerHTML = '';

        glossary.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${escapeHtml(item.title)}</strong></td>
                <td>${escapeHtml(item.term_type || 'Business term')}</td>
                <td>${escapeHtml(item.data_domain || 'General')}</td>
                <td>${escapeHtml(item.description)}</td>
                <td>${escapeHtml(item.examples)}</td>
                <td>${escapeHtml(item.business_logic)}</td>
                <td>${escapeHtml(item.data_type)}</td>
                <td>${escapeHtml(item.technical_aliases)}</td>
                <td>${escapeHtml(item.synonyms)}</td>
                <td>${escapeHtml(item.logical_formula || '-')}</td>
            `;
            glossaryBody.appendChild(row);
        });
    }

    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.scrollIntoView({ behavior: 'smooth' });
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Export to CSV
    exportBtn.addEventListener('click', function() {
        if (currentGlossaryData.length === 0) {
            return;
        }

        const headers = ['Title', 'Term Type', 'Data Domain', 'Description', 'Examples', 'Business Logic', 'Data Type', 'Technical Aliases', 'Synonyms', 'Logical Formula'];

        let csv = headers.join(',') + '\n';

        currentGlossaryData.forEach(item => {
            const row = [
                item.title,
                item.term_type || 'Business term',
                item.data_domain || 'General',
                item.description,
                item.examples,
                item.business_logic,
                item.data_type,
                item.technical_aliases,
                item.synonyms,
                item.logical_formula || ''
            ].map(field => {
                // Escape quotes and wrap in quotes
                const escaped = String(field).replace(/"/g, '""');
                return `"${escaped}"`;
            });

            csv += row.join(',') + '\n';
        });

        // Create download link
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'business_glossary.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    });

    // Drag and drop support
    const fileInputWrapper = document.querySelector('.file-input-wrapper');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        fileInputWrapper.classList.add('highlight');
    }

    function unhighlight(e) {
        fileInputWrapper.classList.remove('highlight');
    }
});
