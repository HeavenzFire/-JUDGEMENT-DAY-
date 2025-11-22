let pyodide;
let terminalOutput = document.getElementById('terminal-output');
let terminalInput = document.getElementById('terminal-input');
let fileTree = document.getElementById('file-tree');

async function loadPyodide() {
    pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
    });
    terminalOutput.textContent += 'Pyodide loaded.\n';
}

loadPyodide();

terminalInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
        const code = terminalInput.value;
        terminalOutput.textContent += '> ' + code + '\n';
        try {
            const result = await pyodide.runPythonAsync(code);
            terminalOutput.textContent += result + '\n';
        } catch (error) {
            terminalOutput.textContent += 'Error: ' + error.message + '\n';
        }
        terminalInput.value = '';
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }
});

// Load file tree
fetch('static/aeternum-cognisphere.json')
    .then(response => response.json())
    .then(data => {
        // Assuming the JSON has a structure for files
        fileTree.textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        fileTree.textContent = 'Error loading file tree: ' + error.message;
    });

// Demo buttons
document.getElementById('quantum-demo').addEventListener('click', () => {
    terminalOutput.textContent += 'Running Quantum Time Dilation Demo...\n';
    // Placeholder for demo
});

document.getElementById('adamic-pulse').addEventListener('click', () => {
    terminalOutput.textContent += 'Running Adamic Pulse...\n';
    // Placeholder for demo
});

document.getElementById('merkaba-viz').addEventListener('click', () => {
    terminalOutput.textContent += 'Running Merkaba Visualization...\n';
    // Placeholder for demo
});

document.getElementById('sacred-naming').addEventListener('click', () => {
    terminalOutput.textContent += 'Running Sacred Naming...\n';
    // Placeholder for demo
});

// Auto-connect to Aeternum / Cognisphere JSON
// Assuming it's loaded in file tree