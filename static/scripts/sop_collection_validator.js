document.addEventListener('DOMContentLoaded', function() {
    const validateButton = document.getElementById('validateButton');
    const clearButton = document.getElementById('clearButton');
    const sopsInput = document.getElementById('sops-input');
    const resultsSection = document.getElementById('results-section');
    const validationOutput = document.getElementById('validation-output');
    const buttonText = validateButton.querySelector('.button-text');
    const buttonLoader = validateButton.querySelector('.button-loader');
    const charCount = document.getElementById('char-count');

    // Character counter
    sopsInput.addEventListener('input', function() {
        charCount.textContent = this.value.length.toLocaleString();
    });

    // Clear button
    clearButton.addEventListener('click', function() {
        sopsInput.value = '';
        charCount.textContent = '0';
        resultsSection.style.display = 'none';
        validationOutput.innerHTML = '';
    });

    // Validate button
    validateButton.addEventListener('click', async function() {
        const sopsContent = sopsInput.value.trim();

        // Validation
        if (!sopsContent) {
            alert('Please provide SOPs content');
            return;
        }

        // Disable button and show loader
        validateButton.disabled = true;
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'inline-block';

        try {
            const response = await fetch('/sop_collection_validator', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'validate_sop_collection',
                    sops_content: sopsContent
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Show results section
                resultsSection.style.display = 'block';
                
                // Format and display the output
                validationOutput.innerHTML = formatValidationOutput(data.validation_result);
                
                // Scroll to results
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while validating the SOP collection. Please try again.');
        } finally {
            // Re-enable button and hide loader
            validateButton.disabled = false;
            buttonText.style.display = 'inline-block';
            buttonLoader.style.display = 'none';
        }
    });

    function formatValidationOutput(text) {
        // Convert markdown-style formatting to HTML
        let formatted = text;
        
        // Headers (### -> h3, ## -> h2)
        formatted = formatted.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        
        // Bold text (**text** -> <strong>text</strong>)
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text (*text* -> <em>text</em>)
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Code blocks (```...``` -> <pre><code>...</code></pre>)
        formatted = formatted.replace(/```(.+?)```/gs, '<pre><code>$1</code></pre>');
        
        // Inline code (`text` -> <code>text</code>)
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Tables (simple markdown tables)
        formatted = formatTables(formatted);
        
        // Bullet points (- text -> <li>text</li>)
        formatted = formatLists(formatted);
        
        // Blockquotes (> text -> <blockquote>text</blockquote>)
        formatted = formatted.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
        
        // Horizontal rules (--- -> <hr>)
        formatted = formatted.replace(/^---$/gm, '<hr>');
        
        // Line breaks
        formatted = formatted.replace(/\n\n/g, '<br><br>');
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }

    function formatTables(text) {
        // Simple table parsing
        const lines = text.split('\n');
        let inTable = false;
        let tableHtml = '';
        let result = [];
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Check if this is a table row (starts and ends with |)
            if (line.startsWith('|') && line.endsWith('|')) {
                if (!inTable) {
                    inTable = true;
                    tableHtml = '<table>';
                }
                
                // Check if this is a separator row (contains only |, -, and spaces)
                if (/^[\|\-\s]+$/.test(line)) {
                    continue; // Skip separator row
                }
                
                // Parse table row
                const cells = line.split('|').filter(cell => cell.trim() !== '');
                const isFirstRow = tableHtml === '<table>';
                
                if (isFirstRow) {
                    tableHtml += '<tr>';
                    cells.forEach(cell => {
                        tableHtml += `<th>${cell.trim()}</th>`;
                    });
                    tableHtml += '</tr>';
                } else {
                    tableHtml += '<tr>';
                    cells.forEach(cell => {
                        tableHtml += `<td>${cell.trim()}</td>`;
                    });
                    tableHtml += '</tr>';
                }
            } else {
                if (inTable) {
                    tableHtml += '</table>';
                    result.push(tableHtml);
                    inTable = false;
                    tableHtml = '';
                }
                result.push(line);
            }
        }
        
        if (inTable) {
            tableHtml += '</table>';
            result.push(tableHtml);
        }
        
        return result.join('\n');
    }

    function formatLists(text) {
        const lines = text.split('<br>');
        let result = [];
        let inList = false;
        
        for (let line of lines) {
            const trimmed = line.trim();
            
            // Check if this is a list item
            if (trimmed.match(/^[-•]\s+(.+)$/)) {
                if (!inList) {
                    result.push('<ul>');
                    inList = true;
                }
                const content = trimmed.replace(/^[-•]\s+/, '');
                result.push(`<li>${content}</li>`);
            } else {
                if (inList) {
                    result.push('</ul>');
                    inList = false;
                }
                if (trimmed) {
                    result.push(line);
                }
            }
        }
        
        if (inList) {
            result.push('</ul>');
        }
        
        return result.join('<br>');
    }

    // Auto-resize textarea
    sopsInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.max(400, this.scrollHeight) + 'px';
    });

    // Handle paste events for better UX
    sopsInput.addEventListener('paste', function(e) {
        setTimeout(() => {
            charCount.textContent = this.value.length.toLocaleString();
        }, 0);
    });
});
