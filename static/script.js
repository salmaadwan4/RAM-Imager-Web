async function startCapture() {
    const investigatorName = document.getElementById('investigatorName').value;
    const investigatorID = document.getElementById('investigatorID').value;
    const caseName = document.getElementById('caseName').value;
    const caseID = document.getElementById('caseID').value;
    const memoryID = document.getElementById('memoryID').value;

    if (!investigatorName || !investigatorID || !caseName || !caseID || !memoryID) {
        showError('All fields are required');
        return;
    }

    const btn = document.getElementById('captureBtn');
    btn.disabled = true;
    btn.innerHTML = `<span class="btn-icon">⏳</span> Capturing...`;
    
    const progressBar = document.querySelector('.progress-bar');
    progressBar.style.width = '0%';
    document.querySelector('.progress-container').style.display = 'block';
    
    try {
        const validationResponse = await fetch('/validate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                investigator_id: investigatorID,
                case_id: caseID,
                memory_id: memoryID
            })
        });
        
        const validationResult = await validationResponse.json();
        if (validationResult.errors.length > 0) {
            showError(validationResult.errors.join('\n'));
            return;
        }
        
        const response = await fetch('/capture', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                investigator_name: investigatorName,
                investigator_id: investigatorID,
                case_name: caseName,
                case_id: caseID,
                memory_id: memoryID
            })
        });
        
        const result = await response.json();
        if (result.status === 'error') {
            throw new Error(result.message);
        }
        
        progressBar.style.width = '100%';
        
        showOutput(`
            🎉 Capture Successful!
            File: ${result.path}
            Size: ${(result.size / 1024 / 1024).toFixed(2)} MB
            SHA256: ${result.hash}
        `);
        
    } catch (error) {
        showError(error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span class="btn-icon">📸</span> Capture Memory`;
    }
}

function showError(message) {
    const output = document.getElementById('outputContainer');
    output.innerHTML = `<div class="error">❌ ${message}</div>`;
    output.style.display = 'block';
}

function showOutput(message) {
    const output = document.getElementById('outputContainer');
    output.innerHTML = `<pre>${message}</pre>`;
    output.style.display = 'block';
}
