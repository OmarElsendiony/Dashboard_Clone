document.addEventListener('DOMContentLoaded', function() {
    const extractButton = document.getElementById('extractButton');
    const clearButton = document.getElementById('clearButton');
    const downloadButton = document.getElementById('downloadButton');
    const draftPolicyInput = document.getElementById('draft-policy-input');
    const resultsSection = document.getElementById('results-section');
    const extractionOutput = document.getElementById('extraction-output');
    const buttonText = extractButton.querySelector('.button-text');
    const buttonLoader = extractButton.querySelector('.button-loader');
    const charCount = document.getElementById('char-count');

    let extractionResultText = '';

    // Character counter
    draftPolicyInput.addEventListener('input', function() {
        charCount.textContent = this.value.length.toLocaleString();
    });

    // Clear button
    clearButton.addEventListener('click', function() {
        draftPolicyInput.value = '';
        charCount.textContent = '0';
        resultsSection.style.display = 'none';
        extractionOutput.innerHTML = '';
        downloadButton.style.display = 'none';
        extractionResultText = '';
    });

    // Download button
    downloadButton.addEventListener('click', function() {
        if (!extractionResultText) return;
        
        const blob = new Blob([extractionResultText], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tool_schemas_' + new Date().toISOString().split('T')[0] + '.txt';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    });

    // Extract button
    extractButton.addEventListener('click', async function() {
        const draftPolicy = draftPolicyInput.value.trim();

        // Validation
        if (!draftPolicy) {
            alert('Please provide draft policy content');
            return;
        }

        // Disable button and show loader
        extractButton.disabled = true;
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'inline-block';

        try {
            const response = await fetch('/clone/tool_schema_extractor', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'extract_tool_schemas',
                    draft_policy: draftPolicy
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Store the raw text for download
                extractionResultText = data.extraction_result;
                
                // Show results section
                resultsSection.style.display = 'block';
                downloadButton.style.display = 'inline-block';
                
                // Format and display the output
                extractionOutput.innerHTML = formatExtractionOutput(data.extraction_result);
                
                // Scroll to results
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while extracting tool schemas. Please try again.');
        } finally {
            // Re-enable button and hide loader
            extractButton.disabled = false;
            buttonText.style.display = 'inline-block';
            buttonLoader.style.display = 'none';
        }
    });

    function formatExtractionOutput(text) {
        // Convert markdown-style formatting to HTML
        let formatted = text;
        
        // Code blocks (```...``` -> <pre><code>...</code></pre>)
        formatted = formatted.replace(/```python\n([\s\S]+?)```/g, '<pre><code>$1</code></pre>');
        formatted = formatted.replace(/```([\s\S]+?)```/g, '<pre><code>$1</code></pre>');
        
        // Headers (#### -> h4, ### -> h3, ## -> h2)
        formatted = formatted.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
        formatted = formatted.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        
        // Bold text (**text** -> <strong>text</strong>)
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text (*text* -> <em>text</em>)
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Inline code (`text` -> <code>text</code>) - but not if already in code block
        formatted = formatted.replace(/`([^`]+)`/g, function(match, p1) {
            // Don't replace if inside <pre> tags
            return '<code>' + p1 + '</code>';
        });
        
        // Tables (simple markdown tables)
        formatted = formatTables(formatted);
        
        // Bullet points (- text -> <li>text</li>)
        formatted = formatLists(formatted);
        
        // Blockquotes (> text -> <blockquote>text</blockquote>)
        formatted = formatted.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
        
        // Horizontal rules (--- -> <hr>)
        formatted = formatted.replace(/^---$/gm, '<hr>');
        
        // Highlight REQUIRED and OPTIONAL
        formatted = formatted.replace(/\bREQUIRED\b/g, '<span class="badge-required">REQUIRED</span>');
        formatted = formatted.replace(/\bOPTIONAL\b/g, '<span class="badge-optional">OPTIONAL</span>');
        
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
            } else if (trimmed.match(/^\d+\.\s+(.+)$/)) {
                // Numbered list
                if (!inList) {
                    result.push('<ol>');
                    inList = true;
                }
                const content = trimmed.replace(/^\d+\.\s+/, '');
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
    draftPolicyInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.max(400, this.scrollHeight) + 'px';
    });

    // Handle paste events for better UX
    draftPolicyInput.addEventListener('paste', function(e) {
        setTimeout(() => {
            charCount.textContent = this.value.length.toLocaleString();
        }, 0);
    });
});
