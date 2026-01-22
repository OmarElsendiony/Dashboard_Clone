// Schema Manager JavaScript

let currentDatabases = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    loadDatabases();
    setupEventListeners();
});

function setupEventListeners() {
    // Action cards
    document.getElementById('add-db-card').addEventListener('click', () => {
        showSection('upload-section');
    });

    document.getElementById('query-db-card').addEventListener('click', () => {
        showSection('query-section');
        loadDatabasesDropdown();
    });

    // File upload
    const fileInput = document.getElementById('schema-zip');
    const dropZone = document.getElementById('drop-zone');

    fileInput.addEventListener('change', function (e) {
        if (e.target.files.length > 0) {
            updateFileName(e.target.files[0].name);
        }
    });

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.name.endsWith('.zip')) {
                fileInput.files = e.dataTransfer.files;
                updateFileName(file.name);
            } else {
                showStatus('upload-status', 'Please drop a valid .zip file', 'error');
            }
        }
    });

    // Upload button
    document.getElementById('upload-btn').addEventListener('click', uploadSchema);

    // Query button
    document.getElementById('query-btn').addEventListener('click', executeQuery);

    // Database select
    document.getElementById('db-select').addEventListener('change', function () {
        const dbName = this.value;
        if (dbName) {
            showDatabaseInfo(dbName);
            document.getElementById('delete-db-btn').style.display = 'inline-block';
        } else {
            document.getElementById('db-info').style.display = 'none';
            document.getElementById('delete-db-btn').style.display = 'none';
        }
    });

    // Delete database button
    document.getElementById('delete-db-btn').addEventListener('click', deleteDatabase);
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });

    // Show selected section
    document.getElementById(sectionId).style.display = 'block';

    // Scroll to section
    document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
}

function closeSection(sectionId) {
    document.getElementById(sectionId).style.display = 'none';
}

function updateFileName(name) {
    document.getElementById('file-name').textContent = name;
    document.getElementById('file-name').style.color = '#667eea';
    document.getElementById('file-name').style.fontWeight = '600';
}

function showStatus(elementId, message, type = 'info') {
    const statusEl = document.getElementById(elementId);
    statusEl.textContent = message;
    statusEl.className = 'status-message ' + type;
    statusEl.style.display = 'block';
}

async function loadDatabases() {
    try {
        const response = await fetch('/clone/schema_manager/list_databases');
        const data = await response.json();

        if (data.status === 'success') {
            currentDatabases = data.databases;
            displayDatabases(data.databases);
        }
    } catch (error) {
        console.error('Error loading databases:', error);
        document.getElementById('db-cards-container').innerHTML =
            '<div class="error">Failed to load databases</div>';
    }
}

function displayDatabases(databases) {
    const container = document.getElementById('db-cards-container');

    if (databases.length === 0) {
        container.innerHTML = '<div class="empty-state">No databases yet. Create your first one!</div>';
        return;
    }

    container.innerHTML = databases.map(db => `
        <div class="db-card" onclick="selectDatabaseForQuery('${db.name}')">
            <div class="db-card-icon">🗄️</div>
            <h4>${db.name}</h4>
            <div class="db-card-info">
                <p><strong>Tables:</strong> ${db.table_count}</p>
                <p><strong>Created:</strong> ${new Date(db.created_at).toLocaleDateString()}</p>
                <p><strong>Data Files:</strong> ${db.data_files_loaded}</p>
            </div>
            <div class="db-card-tables">
                ${db.tables.slice(0, 3).map(t => `<span class="table-tag">${t}</span>`).join('')}
                ${db.tables.length > 3 ? `<span class="table-tag">+${db.tables.length - 3} more</span>` : ''}
            </div>
        </div>
    `).join('');
}

function selectDatabaseForQuery(dbName) {
    showSection('query-section');
    loadDatabasesDropdown();

    setTimeout(() => {
        document.getElementById('db-select').value = dbName;
        showDatabaseInfo(dbName);
        document.getElementById('delete-db-btn').style.display = 'inline-block';
    }, 100);
}

function loadDatabasesDropdown() {
    const select = document.getElementById('db-select');

    select.innerHTML = '<option value="">-- Select a database --</option>';

    currentDatabases.forEach(db => {
        const option = document.createElement('option');
        option.value = db.name;
        option.textContent = `${db.name} (${db.table_count} tables)`;
        select.appendChild(option);
    });
}

function showDatabaseInfo(dbName) {
    const db = currentDatabases.find(d => d.name === dbName);

    if (db) {
        document.getElementById('db-info').style.display = 'block';
        document.getElementById('db-created').textContent = new Date(db.created_at).toLocaleString();
        document.getElementById('db-tables').textContent = db.tables.join(', ');
        document.getElementById('db-data-files').textContent = db.data_files_loaded;
    }
}

async function uploadSchema() {
    const dbName = document.getElementById('db-name').value.trim();
    const fileInput = document.getElementById('schema-zip');

    if (!dbName) {
        showStatus('upload-status', 'Please enter a database name', 'error');
        return;
    }

    if (!fileInput.files || fileInput.files.length === 0) {
        showStatus('upload-status', 'Please select a zip file', 'error');
        return;
    }

    const uploadBtn = document.getElementById('upload-btn');
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Creating Database...';

    showStatus('upload-status', 'Processing schema...', 'info');

    const formData = new FormData();
    formData.append('zipFile', fileInput.files[0]);
    formData.append('dbName', dbName);

    try {
        const response = await fetch('/clone/schema_manager/upload_schema', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            showStatus('upload-status', data.message, 'success');

            // Reset form
            document.getElementById('db-name').value = '';
            fileInput.value = '';
            document.getElementById('file-name').textContent = 'Choose zip file or drag & drop';
            document.getElementById('file-name').style.color = '';
            document.getElementById('file-name').style.fontWeight = '';

            // Reload databases
            await loadDatabases();

            // Show success and close after delay
            setTimeout(() => {
                closeSection('upload-section');
            }, 2000);
        } else {
            showStatus('upload-status', data.message, 'error');
        }
    } catch (error) {
        showStatus('upload-status', 'Error uploading schema: ' + error.message, 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Create Database';
    }
}

async function executeQuery() {
    const dbName = document.getElementById('db-select').value;
    const query = document.getElementById('sql-query').value.trim();

    if (!dbName) {
        showStatus('query-status', 'Please select a database', 'error');
        return;
    }

    if (!query) {
        showStatus('query-status', 'Please enter a query', 'error');
        return;
    }

    const queryBtn = document.getElementById('query-btn');
    queryBtn.disabled = true;
    queryBtn.textContent = 'Executing...';

    showStatus('query-status', 'Running query...', 'info');

    try {
        const response = await fetch('/clone/schema_manager/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dbName: dbName,
                query: query
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showStatus('query-status', `Query executed successfully (${data.count} rows)`, 'success');
            displayResults(data.results);
        } else {
            showStatus('query-status', data.message, 'error');
            document.getElementById('results-container').style.display = 'none';
        }
    } catch (error) {
        showStatus('query-status', 'Error executing query: ' + error.message, 'error');
        document.getElementById('results-container').style.display = 'none';
    } finally {
        queryBtn.disabled = false;
        queryBtn.textContent = 'Execute Query';
    }
}

function displayResults(results) {
    const container = document.getElementById('results-container');
    const thead = document.getElementById('results-thead');
    const tbody = document.getElementById('results-tbody');

    if (!results || results.length === 0) {
        container.style.display = 'block';
        document.getElementById('result-count').textContent = '0';
        thead.innerHTML = '';
        tbody.innerHTML = '<tr><td colspan="100" style="text-align: center; padding: 2rem;">No results</td></tr>';
        return;
    }

    // Get column names from first result
    const columns = Object.keys(results[0]);

    // Create table header
    thead.innerHTML = '<tr>' + columns.map(col =>
        `<th>${col}</th>`
    ).join('') + '</tr>';

    // Create table body
    tbody.innerHTML = results.map(row =>
        '<tr>' + columns.map(col => {
            let value = row[col];

            // Format null values
            if (value === null || value === undefined) {
                return '<td class="null-value">NULL</td>';
            }

            // Format dates
            if (value instanceof Date || (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/))) {
                return `<td class="date-value">${value}</td>`;
            }

            // Format booleans
            if (typeof value === 'boolean') {
                return `<td class="boolean-value">${value ? '✓' : '✗'}</td>`;
            }

            // Format numbers
            if (typeof value === 'number') {
                return `<td class="number-value">${value}</td>`;
            }

            // Truncate long strings
            if (typeof value === 'string' && value.length > 100) {
                return `<td title="${escapeHtml(value)}">${escapeHtml(value.substring(0, 100))}...</td>`;
            }

            return `<td>${escapeHtml(String(value))}</td>`;
        }).join('') + '</tr>'
    ).join('');

    document.getElementById('result-count').textContent = results.length;
    container.style.display = 'block';

    // Scroll to results
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function deleteDatabase() {
    const dbName = document.getElementById('db-select').value;

    if (!dbName) {
        return;
    }

    if (!confirm(`Are you sure you want to delete database "${dbName}"? This action cannot be undone.`)) {
        return;
    }

    const deleteBtn = document.getElementById('delete-db-btn');
    deleteBtn.disabled = true;
    deleteBtn.textContent = 'Deleting...';

    try {
        const response = await fetch('/clone/schema_manager/delete_database', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ dbName: dbName })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showStatus('query-status', data.message, 'success');

            // Reset form
            document.getElementById('db-select').value = '';
            document.getElementById('db-info').style.display = 'none';
            document.getElementById('results-container').style.display = 'none';
            deleteBtn.style.display = 'none';

            // Reload databases
            await loadDatabases();
        } else {
            showStatus('query-status', data.message, 'error');
        }
    } catch (error) {
        showStatus('query-status', 'Error deleting database: ' + error.message, 'error');
    } finally {
        deleteBtn.disabled = false;
        deleteBtn.textContent = 'Delete Database';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}