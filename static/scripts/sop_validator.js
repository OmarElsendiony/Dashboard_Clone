document.addEventListener('DOMContentLoaded', function() {
    const validateButton = document.getElementById('validateButton');
    const sopInput = document.getElementById('sop-input');
    const dataflowInput = document.getElementById('dataflow-input');
    const schemaInput = document.getElementById('schema-input');
    const resultsSection = document.getElementById('results-section');
    const validationStatus = document.getElementById('validation-status');
    const validationOutput = document.getElementById('validation-output');
    const buttonText = validateButton.querySelector('.button-text');
    const buttonLoader = validateButton.querySelector('.button-loader');

    validateButton.addEventListener('click', async function() {
        const sop = sopInput.value.trim();
        const dataFlow = dataflowInput.value.trim();
        const schema = schemaInput.value.trim();

        // Validation
        if (!sop || !dataFlow) {
            alert('Please provide both SOP and Data Flow');
            return;
        }

        // Disable button and show loader
        validateButton.disabled = true;
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'inline-block';

        try {
            const response = await fetch('/clone/sop_validator', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'validate_sop',
                    sop: sop,
                    data_flow: dataFlow,
                    schema: schema
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Show results section
                resultsSection.style.display = 'block';
                
                // Parse the validation result to determine status
                const validationResult = data.validation_result;

                // Check for INVALID first to avoid substring matching issue (INVALID contains VALID)
                const isInvalid = validationResult.toUpperCase().includes('VALIDATION STATUS: INVALID') || 
                                 validationResult.toUpperCase().includes('VALIDATION STATUS**: INVALID') ||
                                 validationResult.toUpperCase().includes('**VALIDATION STATUS**: INVALID');
                
                const isValid = !isInvalid && (
                    validationResult.toUpperCase().includes('VALIDATION STATUS: VALID') ||
                    validationResult.toUpperCase().includes('VALIDATION STATUS**: VALID') ||
                    validationResult.toUpperCase().includes('**VALIDATION STATUS**: VALID')
                );
                
                // Set status badge
                validationStatus.className = 'status-badge ' + (isValid ? 'status-valid' : 'status-invalid');
                validationStatus.textContent = isValid ? '✓ VALID' : '✗ INVALID';
                
                // Format the output with markdown-like rendering
                validationOutput.innerHTML = formatValidationOutput(validationResult);
                
                // Scroll to results
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while validating the SOP. Please try again.');
        } finally {
            // Re-enable button and hide loader
            validateButton.disabled = false;
            buttonText.style.display = 'inline-block';
            buttonLoader.style.display = 'none';
        }
    });

    function formatValidationOutput(text) {
        // Convert markdown-style formatting to HTML
        let formatted = text
            // Bold text (**text** -> <strong>text</strong>)
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Bullet points (- text -> • text)
            .replace(/^- (.+)$/gm, '• $1')
            // Section headers (all caps lines)
            .replace(/^([A-Z\s]+):$/gm, '<h3>$1:</h3>')
            // Line breaks
            .replace(/\n/g, '<br>');
        
        return formatted;
    }

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.max(300, this.scrollHeight) + 'px';
        });
    });
});
