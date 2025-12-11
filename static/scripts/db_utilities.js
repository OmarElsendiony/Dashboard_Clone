async function extract_policy_apis_handling() {
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'extract_policy_apis'
        })
    });

    const data = await response.json();
    console.log(data);

    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = '';
    document.getElementById('content').innerHTML = `
            <h2 id="content-header">Extract Policy APIs</h2>
            <h3 class="content-subheader">Initial Prompt</h3>
            <textarea id="initial-prompt"></textarea>

            <h3 class="content-subheader">Policy</h3>
            <textarea id="policy"></textarea>

            <h3 class="content-subheader">Example APIs</h3>
            <textarea id="example-apis"></textarea>

            <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
                <button id="extract-apis" onclick="sendContentLLM('extract_policy_apis')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Extract Policy APIs</button>
            </div>
        `;

    document.getElementById('initial-prompt').value = data.initial_prompt || '';
    document.getElementById('policy').value = data.policy || '';
    document.getElementById('example-apis').value = data.example_apis || '';
}

async function extract_policy_schema_handling() {
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'extract_policy_schema'
        })
    });

    const data = await response.json();
    console.log(data);

    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = '';
    document.getElementById('content').innerHTML = `
            <h2 id="content-header">Extract Policy Schema</h2>
            <h3 class="content-subheader">Initial Prompt</h3>
            <textarea id="initial-prompt"></textarea>

            <h3 class="content-subheader">Policy</h3>
            <textarea id="policy"></textarea>

            <h3 class="content-subheader">Example Schema</h3>
            <textarea id="example-schema"></textarea>

            <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
                <button id="extract-schema" onclick="sendContentLLM('extract_policy_schema')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Extract Policy Schema</button>
            </div>
        `;

    document.getElementById('initial-prompt').value = data.initial_prompt || '';
    document.getElementById('policy').value = data.policy || '';
    document.getElementById('example-schema').value = data.example_schema || '';
}
async function regression_test_creator_handling() {
    // Fetch data
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'regression_test_creator' })
    });

    const data = await response.json();

    // Render UI
    const contentDiv = document.getElementById('content');
    contentDiv.style.display = 'block';
    contentDiv.innerHTML = '';
    contentDiv.innerHTML = `
        <h2 id="content-header">Regression Test Creator</h2>
        
        <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
            <div style="flex: 1;">
                <h3 class="content-subheader">Environment Name</h3>
                <input type="text" id="environment-name" class="styled-textarea" placeholder="e.g., fund_finance, hr, wiki_pages" style="height:42px;">
            </div>

        </div>
        
        <div id="drop-zone" class="zip-tool-container">
            <div class="zip-tool-header">Project Auto-fill (Drag & Drop Supported)</div>
            
            <div class="control-row">
                <div class="form-group">
                    <label class="styled-label">Interface Version</label>
                    <select id="auto-interface-select" class="styled-select">
                        <option value="1">Interface 1</option>
                        <option value="2">Interface 2</option>
                        <option value="3">Interface 3</option>
                        <option value="4">Interface 4</option>
                        <option value="5">Interface 5</option>
                    </select>
                </div>

                <div class="form-group" style="flex-grow: 1;">
                     <label class="styled-label">Project Zip File</label>
                     
                     <div class="file-input-wrapper">
                        <input type="file" id="auto-zip-input" accept=".zip" class="hidden-file-input">
                        
                        <label for="auto-zip-input" class="custom-file-button">
                            Choose Zip File
                        </label>
                        
                        <span id="file-name-text" class="file-name-display">No file chosen</span>
                     </div>
                </div>
            </div>
            
            <div id="zip-status"></div>
        </div>

        <h3 class="content-subheader">Initial Prompt</h3>
        <textarea id="initial-prompt" class="styled-textarea" style="height:80px;"></textarea>

        <h3 class="content-subheader">Policy</h3>
        <textarea id="policy" class="styled-textarea" style="height:120px;"></textarea>

        <h3 class="content-subheader">Database Schema</h3>
        <textarea id="db-schema" class="styled-textarea" style="height:150px;"></textarea>

        <h3 class="content-subheader">Database Records</h3>
        <textarea id="db-records" class="styled-textarea" style="height:150px;"></textarea>

        <h3 class="content-subheader">Interface Tools</h3>
        <textarea id="interface-tools" class="styled-textarea" style="height:150px;"></textarea>

        <button id="create-test" class="action-btn" onclick="sendContentLLM('regression_test_creator')">
            Generate Regression Test Prompt
        </button>
    `;

    // Fill Defaults
    document.getElementById('environment-name').value = '';
    document.getElementById('initial-prompt').value = data.initial_prompt || '';
    document.getElementById('policy').value = '';
    document.getElementById('db-schema').value = '';
    document.getElementById('db-records').value = '';
    document.getElementById('interface-tools').value = '';

    // ZIP PROCESSING LOGIC
    const processZipFile = async (file) => {
        if (!file) return;

        // Update Filename UI
        const fileNameSpan = document.getElementById('file-name-text');
        fileNameSpan.innerText = file.name;
        fileNameSpan.style.color = "#334155";
        fileNameSpan.style.fontWeight = "600";

        const interfaceNum = document.getElementById('auto-interface-select').value;
        const statusDiv = document.getElementById('zip-status');
        const dbArea = document.getElementById('db-records');
        const toolsArea = document.getElementById('interface-tools');
        const schemaArea = document.getElementById('db-schema');
        const policyArea = document.getElementById('policy');

        statusDiv.innerText = "Processing Zip file...";
        statusDiv.style.color = "#4f46e5";

        try {
            if (typeof JSZip === 'undefined') throw new Error("JSZip library missing.");

            const zip = new JSZip();
            const content = await zip.loadAsync(file);

            let extractedTools = "";
            let extractedData = "";
            let extractedSchema = "";
            let extractedPolicy = "";
            const interfacePathKey = `tools/interface_${interfaceNum}/`;
            const dataPathKey = `data/`;
            const schemaPathKey = `schema/`;
            const policyPathKey = `tools/interface_${interfaceNum}/policy.md`;
            const filePaths = Object.keys(content.files).sort();

            for (const path of filePaths) {
                const entry = content.files[path];
                if (entry.dir || path.includes('__MACOSX')) continue;

                // DATA
                if (path.includes(dataPathKey) && path.endsWith('.json')) {
                    try {
                        const jsonText = await entry.async("string");
                        const jsonData = JSON.parse(jsonText);

                        const cleanFileName = path.split('/').pop();
                        const totalEntries = Array.isArray(jsonData) ? jsonData.length : Object.keys(jsonData).length;

                        let sample = (Array.isArray(jsonData))
                            ? jsonData.slice(0, 10)
                            : Object.keys(jsonData).slice(0, 10).reduce((obj, k) => { obj[k] = jsonData[k]; return obj; }, {});

                        extractedData += `FILE: ${cleanFileName} (Total entries: ${totalEntries})\n` + JSON.stringify(sample, null, 2) + "\n\n";
                    } catch (e) { console.warn(`Skipping ${path}`); }
                }

                // SCHEMA
                if (path.includes(schemaPathKey) && path.endsWith('.json')) {
                    try {
                        const schemaText = await entry.async("string");
                        const cleanFileName = path.split('/').pop();
                        extractedSchema += `FILE: ${cleanFileName}\n` + schemaText + "\n\n";
                    } catch (e) { console.warn(`Skipping schema ${path}`); }
                }

                // POLICY
                if (path.includes(policyPathKey) && path.endsWith('.json')) {
                    try {
                        const policyText = await entry.async("string");
                        // const cleanFileName = path.split('/').pop();
                        extractedPolicy = policyText;
                    } catch (e) { console.warn(`Skipping schema ${path}`); }
                }

                // TOOLS
                if (path.includes(interfacePathKey) && path.endsWith('.py') && !path.endsWith('__init__.py')) {
                    const fullCode = await entry.async("string");
                    const lines = fullCode.split('\n');
                    let extractedLines = [];
                    let capturing = false;
                    let baseIndent = -1;

                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i];
                        if (line.includes('def get_info')) {
                            capturing = true;
                            baseIndent = line.search(/\S/);
                            if (i > 0 && lines[i - 1].trim() === '@staticmethod') extractedLines.push(lines[i - 1]);
                            extractedLines.push(line);
                            continue;
                        }
                        if (capturing) {
                            if (line.trim() === '') { extractedLines.push(line); continue; }
                            if (line.search(/\S/) <= baseIndent) break;
                            extractedLines.push(line);
                        }
                    }
                    if (extractedLines.length > 0) {
                        extractedTools += `# FILE: ${path}\n` + extractedLines.join('\n') + "\n\n";
                    }
                }
            }

            dbArea.value = extractedData || "No JSON data found.";
            toolsArea.value = extractedTools || "No get_info methods found.";
            // schemaArea.value = extractedSchema || "No schema files found.";
            policyArea.value = extractedPolicy || "No policy files found.";

            statusDiv.innerHTML = "<b>Success!</b> Fields populated.";
            statusDiv.style.color = "#166534";

        } catch (err) {
            console.error(err);
            statusDiv.innerText = "Error: " + err.message;
            statusDiv.style.color = "#dc2626";
            fileNameSpan.innerText = "Error loading file";
        }
    };

    // EVENT LISTENERS
    // A. Standard File Input
    document.getElementById('auto-zip-input').addEventListener('change', function (event) {
        processZipFile(event.target.files[0]);
        this.value = '';
    });

    // B. Drag & Drop
    const dropZone = document.getElementById('drop-zone');

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
                processZipFile(file);
            } else {
                alert("Please drop a valid .zip file.");
            }
        }
    });
}

function sendContentLLM(feature) {
    if (feature == "policy_creation") {
        const initialPrompt = document.getElementById('initial-prompt').value;
        const dbSchema = document.getElementById('db-schema').value;
        const examplePolicies = document.getElementById('example-policies').value;
        const interfaceApis = document.getElementById('interface-apis').value;

        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'generate_policy_prompt',
                initial_prompt: initialPrompt,
                db_schema: dbSchema,
                example_policies: examplePolicies,
                interface_apis: interfaceApis
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // remove if they were present before
                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-policy');
                if (existingHeader) {
                    existingHeader.remove();
                }
                if (existingTextArea) {
                    existingTextArea.remove();
                }

                outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Generated Policy Prompt';
                outputHeader.id = 'output-header';
                document.getElementById('content').appendChild(outputHeader);

                textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-policy';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '200px';
                textAreaNode.value = data.prompt;
                document.getElementById('content').appendChild(textAreaNode);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while generating the policy.');
            });
    } else if (feature == "api_implementation") {
        const initialPrompt = document.getElementById('initial-prompt').value;
        const dbSchema = document.getElementById('db-schema').value;
        const exampleApis = document.getElementById('example-apis').value;
        const interfaceApis = document.getElementById('interface-apis').value;

        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'generate_api_prompt',
                initial_prompt: initialPrompt,
                db_schema: dbSchema,
                example_apis: exampleApis,
                interface_apis: interfaceApis
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // remove if they were present before
                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-api');
                if (existingHeader) {
                    existingHeader.remove();
                }
                if (existingTextArea) {
                    existingTextArea.remove();
                }

                outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Generated API Prompt';
                outputHeader.id = 'output-header';
                document.getElementById('content').appendChild(outputHeader);

                textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-api';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '200px';
                textAreaNode.value = data.prompt;
                document.getElementById('content').appendChild(textAreaNode);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while generating the API.');
            });
    } else if (feature == "database_seeding") {
        const initialPrompt = document.getElementById('initial-prompt').value;
        const dbSchema = document.getElementById('db-schema').value;

        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'generate_seed_prompt',
                initial_prompt: initialPrompt,
                db_schema: dbSchema
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // remove if they were present before
                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-seed');
                if (existingHeader) {
                    existingHeader.remove();
                }
                if (existingTextArea) {
                    existingTextArea.remove();
                }

                outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Generated Seed Prompt';
                outputHeader.id = 'output-header';
                document.getElementById('content').appendChild(outputHeader);

                textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-seed';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '200px';
                textAreaNode.value = data.prompt;
                document.getElementById('content').appendChild(textAreaNode);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while generating the seed.');
            });
    } else if (feature == "scenario_realism") {
        const initialPrompt = document.getElementById('initial-prompt').value;
        const dbSchema = document.getElementById('db-schema').value;

        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'check_scenario_realism',
                initial_prompt: initialPrompt,
                db_schema: dbSchema,
                scenario: document.getElementById('scenario').value
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // remove if they were present before
                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-scenario');
                if (existingHeader) {
                    existingHeader.remove();
                }
                if (existingTextArea) {
                    existingTextArea.remove();
                }

                outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Generated Scenario Prompt';
                outputHeader.id = 'output-header';
                document.getElementById('content').appendChild(outputHeader);

                textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-scenario';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '200px';
                textAreaNode.value = data.realism_check;
                document.getElementById('content').appendChild(textAreaNode);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while generating the scenario.');
            });
    } else if (feature == "extract_policy_apis") {
        const initialPrompt = document.getElementById('initial-prompt').value;
        const policy = document.getElementById('policy').value;
        const exampleApis = document.getElementById('example-apis').value;

        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'extract_policy_apis',
                initial_prompt: initialPrompt,
                policy: policy,
                example_apis: exampleApis
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // remove if they were present before
                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-apis');
                if (existingHeader) {
                    existingHeader.remove();
                }
                if (existingTextArea) {
                    existingTextArea.remove();
                }

                outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Extracted Policy APIs';
                outputHeader.id = 'output-header';
                document.getElementById('content').appendChild(outputHeader);

                textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-prompt';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '200px';
                textAreaNode.value = data.prompt;
                document.getElementById('content').appendChild(textAreaNode);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while extracting policy APIs.');
            });
    } else if (feature == "extract_policy_schema") {
        const initialPrompt = document.getElementById('initial-prompt').value;
        const policy = document.getElementById('policy').value;
        const exampleSchema = document.getElementById('example-schema').value;

        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'extract_policy_schema',
                initial_prompt: initialPrompt,
                policy: policy,
                example_schema: exampleSchema
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // remove if they were present before
                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-schema');
                if (existingHeader) {
                    existingHeader.remove();
                }
                if (existingTextArea) {
                    existingTextArea.remove();
                }

                outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Extracted Policy Schema';
                outputHeader.id = 'output-header';
                document.getElementById('content').appendChild(outputHeader);

                textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-prompt';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '200px';
                textAreaNode.value = data.prompt;
                document.getElementById('content').appendChild(textAreaNode);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while extracting policy schema.');
            });
    } else if (feature == "tune_policy") {
        const initialPrompt = document.getElementById('initial-prompt').value;
        const policy = document.getElementById('policy').value;
        const examplePolicies = document.getElementById('example-policies').value;

        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'tune_policy',
                initial_prompt: initialPrompt,
                policy: policy,
                example_policies: examplePolicies
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // remove if they were present before
                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-tuned-policy');
                if (existingHeader) {
                    existingHeader.remove();
                }
                if (existingTextArea) {
                    existingTextArea.remove();
                }

                outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Tuned Policy';
                outputHeader.id = 'output-header';
                document.getElementById('content').appendChild(outputHeader);

                textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-tuned-policy';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '200px';
                textAreaNode.value = data.prompt;
                document.getElementById('content').appendChild(textAreaNode);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while tuning the policy.');
            });
    } else if (feature == "policy_validator") {
        const initialPrompt = document.getElementById('initial-prompt').value;
        const policy = document.getElementById('policy').value;
        const examplePolicies = document.getElementById('example-policies').value;

        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'validate_policy',
                initial_prompt: initialPrompt,
                policy: policy,
                example_policies: examplePolicies
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // remove if they were present before
                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-validation');
                if (existingHeader) {
                    existingHeader.remove();
                }
                if (existingTextArea) {
                    existingTextArea.remove();
                }

                outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Policy Validation Results';
                outputHeader.id = 'output-header';
                document.getElementById('content').appendChild(outputHeader);

                textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-validation';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '200px';
                textAreaNode.value = data.prompt;
                document.getElementById('content').appendChild(textAreaNode);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while validating the policy.');
            });
    } else if (feature == "sop_task_creator") {
        // 1. Gather Inputs
        const initialPrompt = document.getElementById('initial-prompt').value;
        const policy = document.getElementById('policy').value;
        const targetSops = document.getElementById('target-sops').value;
        const dbRecords = document.getElementById('db-records').value;
        const interfaceTools = document.getElementById('interface-tools').value;
        const exampleTasks = document.getElementById('example-tasks').value;

        // 2. Validation
        if (!targetSops.trim()) {
            alert('Please specify target SOP numbers (e.g., 1, 2, 6, 9) before generating.');
            return;
        }

        // 3. Send Request
        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'generate_sop_task_prompt',
                initial_prompt: initialPrompt,
                policy: policy,
                target_sops: targetSops,
                db_records: dbRecords,
                interface_tools: interfaceTools,
                example_tasks: exampleTasks
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);

                // 4. Handle Output Display
                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-task');
                if (existingHeader) existingHeader.remove();
                if (existingTextArea) existingTextArea.remove();

                const outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Generated Task Prompt';
                outputHeader.id = 'output-header';
                outputHeader.style.marginTop = '2rem';
                outputHeader.style.borderTop = '1px solid #eee';
                outputHeader.style.paddingTop = '1rem';
                document.getElementById('content').appendChild(outputHeader);

                const textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-task';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '300px'; // Made slightly taller for results
                textAreaNode.style.padding = '1rem';
                textAreaNode.style.marginTop = '1rem';
                textAreaNode.style.borderRadius = '8px';
                textAreaNode.style.border = '1px solid #ccc';
                textAreaNode.value = data.prompt;

                document.getElementById('content').appendChild(textAreaNode);

                // Scroll to the result
                textAreaNode.scrollIntoView({ behavior: 'smooth' });
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while generating the task prompt.');
            });
    } else if (feature == "regression_test_creator") {
        const environmentName = document.getElementById('environment-name').value;
        const interfaceNum = document.getElementById('auto-interface-select').value;
        const initialPrompt = document.getElementById('initial-prompt').value;
        const policy = document.getElementById('policy').value;
        const dbSchema = document.getElementById('db-schema').value;
        const dbRecords = document.getElementById('db-records').value;
        const interfaceTools = document.getElementById('interface-tools').value;

        // Validation
        if (!environmentName.trim()) {
            alert('Please specify the environment name before generating.');
            return;
        }

        fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'generate_regression_test_prompt',
                environment_name: environmentName,
                interface_number: interfaceNum,
                initial_prompt: initialPrompt,
                policy: policy,
                db_schema: dbSchema,
                db_records: dbRecords,
                interface_tools: interfaceTools
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);

                const existingHeader = document.getElementById('output-header');
                const existingTextArea = document.getElementById('generated-test');
                if (existingHeader) existingHeader.remove();
                if (existingTextArea) existingTextArea.remove();

                const outputHeader = document.createElement('h2');
                outputHeader.innerText = 'Generated Regression Test Prompt';
                outputHeader.id = 'output-header';
                outputHeader.style.marginTop = '2rem';
                outputHeader.style.borderTop = '1px solid #eee';
                outputHeader.style.paddingTop = '1rem';
                document.getElementById('content').appendChild(outputHeader);

                const textAreaNode = document.createElement('textarea');
                textAreaNode.id = 'generated-test';
                textAreaNode.style.width = '100%';
                textAreaNode.style.height = '300px';
                textAreaNode.style.padding = '1rem';
                textAreaNode.style.marginTop = '1rem';
                textAreaNode.style.borderRadius = '8px';
                textAreaNode.style.border = '1px solid #ccc';
                textAreaNode.value = data.prompt;

                document.getElementById('content').appendChild(textAreaNode);

                textAreaNode.scrollIntoView({ behavior: 'smooth' });
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while generating the regression test prompt.');
            });
    } else {
        alert("This feature is not implemented yet.");
    }
}

async function policy_creation_handling() {
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'policy_creation'
        })
    });

    const data = await response.json();
    console.log(data);

    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = '';
    document.getElementById('content').innerHTML = `
            <h2 id="content-header">Policy Creation</h2>
            <h3 class="content-subheader">Initial Prompt</h3>
            <textarea id="initial-prompt"></textarea>

            <h3 class="content-subheader">Database schema</h3>
            <textarea id="db-schema"></textarea>

            <h3 class="content-subheader">Example policies</h3>
            <textarea id="example-policies"></textarea>

            <h3 class="content-subheader">Interface APIs</h3>
            <textarea id="interface-apis"></textarea>
            <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
                <button id="generate-policy" onclick="sendContentLLM('policy_creation')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Generate Policy Prompt</button>
            </div>
        `;

    document.getElementById('initial-prompt').value = data.initial_prompt;
    // document.getElementById('db-schema').value = data.db_schema;
    document.getElementById('example-policies').value = data.example_policies;
}

async function database_seeding_handling() {
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'database_seeding'
        })
    });

    const data = await response.json();
    console.log(data);

    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = '';
    document.getElementById('content').innerHTML = `
            <h2 id="content-header">Database Seeding</h2>
            <h3 class="content-subheader">Initial Prompt</h3>
            <textarea id="initial-prompt"></textarea>

            <h3 class="content-subheader">Database schema</h3>
            <textarea id="db-schema"></textarea>

            <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
                <button id="generate-seed" onclick="sendContentLLM('database_seeding')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Generate Seed Prompt</button>
            </div>
        `;

    document.getElementById('initial-prompt').value = data.initial_prompt;
    // document.getElementById('db-schema').value = data.db_schema;
    // document.getElementById('example-data').value = data.example_data;
}

// async function scenario_realism_handling() {
//     const response = await fetch('/database_utilities', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({
//             action: 'scenario_realism'
//         })
//     });

//     const data = await response.json();
//     console.log(data);

//     document.getElementById('content').style.display = 'block';
//     document.getElementById('content').innerHTML = '';
//     document.getElementById('content').innerHTML = `
//             <h2 id="content-header">Scenario Realism</h2>
//             <h3 class="content-subheader">Initial Prompt</h3>
//             <textarea id="initial-prompt"></textarea>

//             <h3 class="content-subheader">Database schema</h3>
//             <textarea id="db-schema"></textarea>

//             <h3 class="content-subheader">Scenario</h3>
//             <textarea id="scenario"></textarea>

//             <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
//                 <button id="generate-scenario" onclick="sendContentLLM('scenario_realism')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Generate Scenario Prompt</button>
//             </div>
//         `;

//     document.getElementById('initial-prompt').value = data.initial_prompt;
//     // document.getElementById('db-schema').value = data.db_schema;
// }

async function api_implementation_handling() {

    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'api_implementation'
        })
    });

    const data = await response.json();
    console.log(data);

    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = '';
    document.getElementById('content').innerHTML = `
            <h2 id="content-header">API Implementation</h2>
            <h3 class="content-subheader">Initial Prompt</h3>
            <textarea id="initial-prompt"></textarea>

            <h3 class="content-subheader">Database schema</h3>
            <textarea id="db-schema"></textarea>

            <h3 class="content-subheader">Example APIs</h3>
            <textarea id="example-apis"></textarea>

            <h3 class="content-subheader">Interface APIs</h3>
            <textarea id="interface-apis"></textarea>

            <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
                <button id="generate-api" onclick="sendContentLLM('api_implementation')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Generate API Prompt</button>
            </div>
        `;

    document.getElementById('initial-prompt').value = data.initial_prompt;
    // document.getElementById('db-schema').value = data.db_schema;
    document.getElementById('example-apis').value = data.example_apis;

}


async function extract_policy_apis_handling() {
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'extract_policy_apis'
        })
    });

    const data = await response.json();
    console.log(data);

    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = '';
    document.getElementById('content').innerHTML = `
            <h2 id="content-header">Extract Policy APIs</h2>
            <h3 class="content-subheader">Initial Prompt</h3>
            <textarea id="initial-prompt"></textarea>

            <h3 class="content-subheader">Policy</h3>
            <textarea id="policy"></textarea>

            <h3 class="content-subheader">Example APIs</h3>
            <textarea id="example-apis"></textarea>

            <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
                <button id="extract-apis" onclick="sendContentLLM('extract_policy_apis')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Extract Policy APIs</button>
            </div>
        `;

    document.getElementById('initial-prompt').value = data.initial_prompt || '';
    document.getElementById('policy').value = data.policy || '';
    document.getElementById('example-apis').value = data.example_apis || '';
}

async function tune_policy_handling() {
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'tune_policy'
        })
    });

    const data = await response.json();
    console.log(data);

    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = '';
    document.getElementById('content').innerHTML = `
            <h2 id="content-header">Tune Policy</h2>
            <h3 class="content-subheader">Initial Prompt</h3>
            <textarea id="initial-prompt"></textarea>

            <h3 class="content-subheader">Policy</h3>
            <textarea id="policy"></textarea>

            <h3 class="content-subheader">Example Policies</h3>
            <textarea id="example-policies"></textarea>

            <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
                <button id="tune-policy" onclick="sendContentLLM('tune_policy')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Tune Policy</button>
            </div>
        `;

    document.getElementById('initial-prompt').value = data.initial_prompt || '';
    document.getElementById('policy').value = data.policy || '';
    document.getElementById('example-policies').value = data.example_policies || '';
}

async function policy_validator_handling() {
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'policy_validator'
        })
    });

    const data = await response.json();
    console.log(data);

    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = '';
    document.getElementById('content').innerHTML = `
            <h2 id="content-header">Policy Validator</h2>
            <h3 class="content-subheader">Initial Prompt</h3>
            <textarea id="initial-prompt"></textarea>

            <h3 class="content-subheader">Policy</h3>
            <textarea id="policy"></textarea>

            <h3 class="content-subheader">Example Policies</h3>
            <textarea id="example-policies"></textarea>

            <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
                <button id="validate-policy" onclick="sendContentLLM('policy_validator')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Validate Policy</button>
            </div>
        `;

    document.getElementById('initial-prompt').value = data.initial_prompt || '';
    document.getElementById('policy').value = data.policy || '';
    document.getElementById('example-policies').value = data.example_policies || '';
}

async function extract_policy_schema_handling() {
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'extract_policy_schema'
        })
    });

    const data = await response.json();
    console.log(data);

    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = '';
    document.getElementById('content').innerHTML = `
            <h2 id="content-header">Extract Policy Schema</h2>
            <h3 class="content-subheader">Initial Prompt</h3>
            <textarea id="initial-prompt"></textarea>

            <h3 class="content-subheader">Policy</h3>
            <textarea id="policy"></textarea>

            <h3 class="content-subheader">Example Schema</h3>
            <textarea id="example-schema"></textarea>

            <div style="display: flex; justify-content: center; align-items: center; margin-top: 1rem;">
                <button id="extract-schema" onclick="sendContentLLM('extract_policy_schema')" style="margin: 1rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">Extract Policy Schema</button>
            </div>
        `;

    document.getElementById('initial-prompt').value = data.initial_prompt || '';
    document.getElementById('policy').value = data.policy || '';
    document.getElementById('example-schema').value = data.example_schema || '';
}


document.addEventListener('DOMContentLoaded', function () {
    // Add click handlers for utility cards
    const cards = document.querySelectorAll('.analytics-card');
    cards.forEach(card => {
        card.addEventListener('click', function () {
            const utility = this.dataset.utility;
            if (utility) {
                console.log(`Clicked on ${utility}`);
                // Add navigation logic here
                if (utility === 'policy-creation') {
                    policy_creation_handling();
                } else if (utility === 'api-implementation') {
                    api_implementation_handling();
                } else if (utility === 'database-seeding') {
                    database_seeding_handling();
                } else if (utility === 'scenario-realism') {
                    scenario_realism_handling();
                }
                else if (utility === 'extract-policy-apis') {
                    extract_policy_apis_handling();
                } else if (utility === 'extract-policy-schema') {
                    extract_policy_schema_handling();
                }
                else if (utility === 'tune-policy') {
                    tune_policy_handling();
                } else if (utility === 'policy-validator') {
                    policy_validator_handling();
                } else if (utility === 'sop-task-creator') {
                    sop_task_creator_handling();
                }
                else if (utility === 'regression-test-creator') {
                    regression_test_creator_handling();
                }
            } else {
                console.warn('No utility data found for this card.');
            }
        });
    });
});

async function sop_task_creator_handling() {
    // 1. Fetch data
    const response = await fetch('/database_utilities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'sop_task_creator' })
    });

    const data = await response.json();

    // 2. Render UI
    const contentDiv = document.getElementById('content');
    contentDiv.style.display = 'block';
    contentDiv.innerHTML = '';
    contentDiv.innerHTML = `
        <h2 id="content-header">SOP-based Task Creator</h2>
        
        <div id="drop-zone" class="zip-tool-container">
            <div class="zip-tool-header">Project Auto-fill (Drag & Drop Supported)</div>
            
            <div class="control-row">
                <div class="form-group">
                    <label class="styled-label">Interface Version</label>
                    <select id="auto-interface-select" class="styled-select">
                        <option value="1">Interface 1</option>
                        <option value="2">Interface 2</option>
                        <option value="3">Interface 3</option>
                        <option value="4">Interface 4</option>
                        <option value="5">Interface 5</option>
                    </select>
                </div>

                <div class="form-group" style="flex-grow: 1;">
                     <label class="styled-label">Project Zip File</label>
                     
                     <div class="file-input-wrapper">
                        <input type="file" id="auto-zip-input" accept=".zip" class="hidden-file-input">
                        
                        <label for="auto-zip-input" class="custom-file-button">
                            Choose Zip File
                        </label>
                        
                        <span id="file-name-text" class="file-name-display">No file chosen</span>
                     </div>
                </div>
            </div>
            
            <div id="zip-status"></div>
        </div>

        <h3 class="content-subheader">Initial Prompt</h3>
        <textarea id="initial-prompt" class="styled-textarea" style="height:80px;"></textarea>

        <h3 class="content-subheader">Policy</h3>
        <textarea id="policy" class="styled-textarea" style="height:120px;"></textarea>

        <h3 class="content-subheader">Target SOPs</h3>
        <input type="text" id="target-sops" placeholder="e.g. 1, 2, 6, 9" class="styled-textarea" style="height:42px;">

        <h3 class="content-subheader">Database Records</h3>
        <textarea id="db-records" class="styled-textarea" style="height:150px;"></textarea>

        <h3 class="content-subheader">Interface Tools</h3>
        <textarea id="interface-tools" class="styled-textarea" style="height:150px;"></textarea>

        <h3 class="content-subheader">Example Tasks</h3>
        <textarea id="example-tasks" class="styled-textarea" style="height:120px;"></textarea>

        <button id="create-task" class="action-btn" onclick="sendContentLLM('sop_task_creator')">
            Generate Task Prompt
        </button>
    `;

    // 3. Fill Defaults
    document.getElementById('initial-prompt').value = data.initial_prompt || '';
    document.getElementById('policy').value = data.policy || '';
    document.getElementById('target-sops').value = '';
    document.getElementById('db-records').value = data.db_records || '';
    document.getElementById('interface-tools').value = data.interface_tools || '';
    document.getElementById('example-tasks').value = data.example_tasks || '';

    // ==========================================
    // 4. SHARED ZIP PROCESSING LOGIC
    // ==========================================
    // ==========================================
    // 4. SHARED ZIP PROCESSING LOGIC (UPDATED)
    // ==========================================
    const processZipFile = async (file) => {
        if (!file) return;

        // Update Filename UI
        const fileNameSpan = document.getElementById('file-name-text');
        fileNameSpan.innerText = file.name;
        fileNameSpan.style.color = "#334155";
        fileNameSpan.style.fontWeight = "600";

        const interfaceNum = document.getElementById('auto-interface-select').value;
        const statusDiv = document.getElementById('zip-status');
        const dbArea = document.getElementById('db-records');
        const toolsArea = document.getElementById('interface-tools');

        statusDiv.innerText = "Processing Zip file...";
        statusDiv.style.color = "#4f46e5";

        try {
            if (typeof JSZip === 'undefined') throw new Error("JSZip library missing.");

            const zip = new JSZip();
            const content = await zip.loadAsync(file);

            let extractedTools = "";
            let extractedData = "";
            const interfacePathKey = `tools/interface_${interfaceNum}/`;
            const dataPathKey = `data/`;

            const filePaths = Object.keys(content.files).sort();

            for (const path of filePaths) {
                const entry = content.files[path];
                if (entry.dir || path.includes('__MACOSX')) continue;

                // DATA
                if (path.includes(dataPathKey) && path.endsWith('.json')) {
                    try {
                        const jsonText = await entry.async("string");
                        const jsonData = JSON.parse(jsonText);

                        // --- NEW LOGIC START ---
                        // 1. Get the "last name" (filename only, no path)
                        const cleanFileName = path.split('/').pop();

                        // 2. Get total number of entries
                        const totalEntries = Array.isArray(jsonData) ? jsonData.length : Object.keys(jsonData).length;
                        // --- NEW LOGIC END ---

                        let sample = (Array.isArray(jsonData))
                            ? jsonData.slice(0, 10)
                            : Object.keys(jsonData).slice(0, 10).reduce((obj, k) => { obj[k] = jsonData[k]; return obj; }, {});

                        // 3. Updated Output Format
                        extractedData += `FILE: ${cleanFileName} (Total entries: ${totalEntries})\n` + JSON.stringify(sample, null, 2) + "\n\n";
                    } catch (e) { console.warn(`Skipping ${path}`); }
                }

                // TOOLS
                if (path.includes(interfacePathKey) && path.endsWith('.py') && !path.endsWith('__init__.py')) {
                    const fullCode = await entry.async("string");
                    const lines = fullCode.split('\n');
                    let extractedLines = [];
                    let capturing = false;
                    let baseIndent = -1;

                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i];
                        if (line.includes('def get_info')) {
                            capturing = true;
                            baseIndent = line.search(/\S/);
                            if (i > 0 && lines[i - 1].trim() === '@staticmethod') extractedLines.push(lines[i - 1]);
                            extractedLines.push(line);
                            continue;
                        }
                        if (capturing) {
                            if (line.trim() === '') { extractedLines.push(line); continue; }
                            if (line.search(/\S/) <= baseIndent) break;
                            extractedLines.push(line);
                        }
                    }
                    if (extractedLines.length > 0) {
                        extractedTools += `# FILE: ${path}\n` + extractedLines.join('\n') + "\n\n";
                    }
                }
            }

            dbArea.value = extractedData || "No JSON data found.";
            toolsArea.value = extractedTools || "No get_info methods found.";

            statusDiv.innerHTML = "<b>Success!</b> Fields populated.";
            statusDiv.style.color = "#166534";

        } catch (err) {
            console.error(err);
            statusDiv.innerText = "Error: " + err.message;
            statusDiv.style.color = "#dc2626";
            fileNameSpan.innerText = "Error loading file";
        }
    };

    // ==========================================
    // 5. EVENT LISTENERS
    // ==========================================

    // A. Standard File Input
    document.getElementById('auto-zip-input').addEventListener('change', function (event) {
        processZipFile(event.target.files[0]);
        this.value = '';
    });

    // B. Drag & Drop
    const dropZone = document.getElementById('drop-zone');

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
                processZipFile(file);
            } else {
                alert("Please drop a valid .zip file.");
            }
        }
    });
}

// ... (previous event listener code remains the same)

function renderSopTaskCreatorForm(initialPrompt, exampleTasks) {
    const contentDiv = document.getElementById('content');

    // HTML Template for the Inputs (Model Selector Removed)
    contentDiv.innerHTML = `
        <div class="utility-form-container">
            <h2>SOP-based Task Creator</h2>
            
            <div class="form-row">
                <div class="form-group half-width">
                    <label>Target SOPs (comma separated):</label>
                    <input type="text" id="target_sops" class="form-control" placeholder="e.g., UserCreation, PasswordReset">
                </div>
                <div class="form-group half-width">
                    <label>Database Records (Context):</label>
                    <textarea id="db_records" class="form-control" rows="3" placeholder="JSON or Schema context..."></textarea>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group half-width">
                    <label>Policy:</label>
                    <textarea id="policy" class="form-control" rows="5" placeholder="Paste policy content here..."></textarea>
                </div>
                <div class="form-group half-width">
                    <label>Interface Tools:</label>
                    <textarea id="interface_tools" class="form-control" rows="5" placeholder="List available tools/APIs..."></textarea>
                </div>
            </div>

            <input type="hidden" id="initial_prompt_template" value="${escapeHtml(initialPrompt)}">
            <input type="hidden" id="example_tasks_template" value="${escapeHtml(exampleTasks)}">

            <button id="generate-btn" class="action-btn">Generate Task Prompt</button>

            <div id="result-section" style="display:none; margin-top: 20px;">
                <h3>Generation Result</h3>
                <div class="result-box">
                    <pre id="llm-output"></pre>
                </div>
                <button onclick="copyToClipboard()" class="copy-btn">Copy Result</button>
            </div>
        </div>
    `;

    // Attach Event Listener to the Generate Button
    document.getElementById('generate-btn').addEventListener('click', submitSopTaskGeneration);
}

async function submitSopTaskGeneration() {
    const generateBtn = document.getElementById('generate-btn');
    const resultSection = document.getElementById('result-section');
    const outputPre = document.getElementById('llm-output');

    // UI Loading State
    generateBtn.disabled = true;
    generateBtn.innerText = 'Generating... (this may take a moment)';
    resultSection.style.display = 'none';

    const payload = {
        action: 'generate_sop_task_prompt',
        model: 'claude-sonnet-4-20250514', // Hardcoded default model since selector is removed
        target_sops: document.getElementById('target_sops').value,
        db_records: document.getElementById('db_records').value,
        policy: document.getElementById('policy').value,
        interface_tools: document.getElementById('interface_tools').value,
        // Pass the templates back to the backend
        initial_prompt: document.getElementById('initial_prompt_template').value,
        example_tasks: document.getElementById('example_tasks_template').value
    };

    try {
        const response = await fetch('/database_utilities_prompt_generation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.status === 'success') {
            resultSection.style.display = 'block';
            outputPre.textContent = data.generation_result;
        } else {
            alert('Error: ' + data.message);
        }

    } catch (e) {
        alert('Request failed: ' + e);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerText = 'Generate Task Prompt';
    }
}

// ... (Rest of the helper functions like escapeHtml and copyToClipboard remain the same)
// Helper to prevent XSS when injecting values into hidden inputs
function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function copyToClipboard() {
    const text = document.getElementById('llm-output').textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert("Copied to clipboard!");
    });
}