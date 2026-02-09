// --- File Input UI ---
document.getElementById('fileInput').addEventListener('change', function() {
    let count = this.files.length;
    let text = count > 0 ? `${count} files selected` : "No files chosen";
    document.getElementById('fileName').textContent = text;
});

// --- Terminal Logic ---

// Keep track of how many logs we have shown so we don't duplicate
let seenLogs = 0;

function fetchLogs() {
    fetch('/get_logs')
        .then(response => response.json())
        .then(data => {
            const termBody = document.getElementById('terminalOutput');
            
            // Only append new logs
            if (data.length > seenLogs) {
                // Get the slice of new logs
                const newLogs = data.slice(seenLogs);
                
                newLogs.forEach(log => {
                    const line = document.createElement('div');
                    line.className = 'log-line';
                    
                    let colorClass = "";
                    if(log.level === "ERROR" || log.level === "CRITICAL") colorClass = "log-error";
                    if(log.level === "SUCCESS") colorClass = "log-success";
                    if(log.level === "NETWORK") colorClass = "log-network";

                    line.innerHTML = `
                        <span class="log-time">[${log.time}]</span> 
                        <span class="${colorClass}">${log.message}</span>
                    `;
                    termBody.appendChild(line);
                });
                
                // Auto scroll to bottom
                termBody.scrollTop = termBody.scrollHeight;
                seenLogs = data.length;
            }
        });
}

// Poll logs every 1 second
setInterval(fetchLogs, 1000);

// --- System Status Check ---
function checkStatus() {
    fetch('/system_status')
        .then(response => response.json())
        .then(data => {
            const indicator = document.getElementById('systemStatus');
            const text = document.getElementById('statusText');
            
            if (data.status === 'online') {
                indicator.style.backgroundColor = '#10b981'; // Green
                indicator.style.boxShadow = '0 0 8px #10b981';
                text.textContent = "SYSTEM_ONLINE";
                text.style.color = "#10b981";
            } else {
                indicator.style.backgroundColor = '#ef4444'; // Red
                indicator.style.boxShadow = '0 0 8px #ef4444';
                text.textContent = "GRID_OFFLINE";
                text.style.color = "#ef4444";
            }
        });
}

// Check status every 3 seconds
setInterval(checkStatus, 3000);
checkStatus(); // Run immediately on load


// --- TERMINAL CONTROLS ---

// 1. Clear Terminal
function clearTerminal() {
    const termBody = document.getElementById('terminalOutput');
    termBody.innerHTML = '<div class="log-line"><span class="log-time mono">[SYSTEM]</span> Console cleared.</div>';
}

// 2. Toggle Terminal (Minimize/Maximize)
function toggleTerminal() {
    const win = document.getElementById('terminalWindow');
    const launcher = document.getElementById('terminalLauncher');
    
    if (win.classList.contains('hidden')) {
        win.classList.remove('hidden');
        if(launcher) launcher.classList.add('hidden');
        // Reset position if off-screen (safety)
        if(win.style.top === "" && win.style.bottom === "") { 
            win.style.bottom = "20px"; 
            win.style.right = "20px";
        }
    } else {
        win.classList.add('hidden');
        if(launcher) launcher.classList.remove('hidden');
    }
}

// 3. Draggable Logic
const terminalWindow = document.getElementById("terminalWindow");
if(terminalWindow) {
    dragElement(terminalWindow);
}

function dragElement(elmnt) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    const header = document.getElementById("terminalHeader");
    
    if (header) {
        header.onmousedown = dragMouseDown;
    } else {
        elmnt.onmousedown = dragMouseDown;
    }

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        
        elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
        elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
        elmnt.style.bottom = "auto";
        elmnt.style.right = "auto";
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
    }
}


// --- Batch Image Processing ---

document.getElementById('imageForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    const resultArea = document.getElementById('resultArea');
    const resultsTitle = document.getElementById('resultsTitle');

    if (files.length === 0) {
        alert("Please select at least one image.");
        return;
    }

    // Reset UI for new batch
    resultArea.innerHTML = "";
    resultArea.classList.remove('hidden');
    if(resultsTitle) resultsTitle.classList.remove('hidden');

    // Process each file individually
    for (let i = 0; i < files.length; i++) {
        processSingleImage(files[i]);
    }
});

async function processSingleImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    const resultArea = document.getElementById('resultArea');
    const placeholderId = `card-${Date.now()}-${Math.random()}`;
    
    const cardHTML = `
        <div id="${placeholderId}" class="result-card" style="opacity: 0.5;">
            <div style="height: 140px; background: #111; display: flex; align-items: center; justify-content: center; color: #444;">
                <span class="mono">UPLOADING...</span>
            </div>
            <div class="result-meta">
                <div class="meta-row"><span>FILE</span> <span>${file.name}</span></div>
            </div>
        </div>
    `;
    resultArea.insertAdjacentHTML('beforeend', cardHTML);

    try {
        const response = await fetch('/process_image', { method: 'POST', body: formData });
        const data = await response.json();
        
        const card = document.getElementById(placeholderId);

        if (data.status === 'success') {
            card.style.opacity = "1";
            card.style.borderColor = "#059669"; 
            let shortNode = data.node.replace("http://", "").replace("127.0.0.1", "LOCALHOST");
            
            // UPDATED: Added 'worker-id' class to the Time span to match blue color
            card.innerHTML = `
                <img src="${data.processed_url}" onclick="window.open('${data.processed_url}')" style="cursor: pointer;">
                <div class="result-meta">
                    <div class="meta-row"><span>FILE</span> <span>${file.name}</span></div>
                    <div class="meta-row">
                        <span>NODE</span> 
                        <span class="worker-id">${shortNode}</span>
                    </div>
                    <div class="meta-row">
                        <span>TIME</span> 
                        <span class="worker-id">${data.time}</span>
                    </div>
                </div>
            `;
        } else {
            card.style.borderColor = "#be123c"; 
            card.innerHTML = `
                 <div style="height: 140px; background: #221; display: flex; align-items: center; justify-content: center; color: #be123c;">
                    <span class="mono">FAILED</span>
                </div>
                <div class="result-meta">
                    <div class="meta-row"><span>ERR</span> <span>Server Error</span></div>
                </div>
            `;
        }
    } catch (error) {
        console.error(error);
    }
}

// --- Password Cracking Logic ---

document.getElementById('crackForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const resultArea = document.getElementById('resultArea');
    const resultsTitle = document.getElementById('resultsTitle');

    resultArea.innerHTML = "";
    resultArea.classList.remove('hidden');
    if(resultsTitle) resultsTitle.classList.remove('hidden');

    resultArea.innerHTML = `
        <div class="result-card" style="width: 100%; grid-column: 1 / -1; padding: 2rem; text-align: center;">
             <span class="mono" style="color: var(--accent);">/// INITIATING_GRID_SEARCH...</span>
        </div>
    `;

    try {
        const response = await fetch('/crack_password', { method: 'POST', body: formData });
        const data = await response.json();

        if (data.status === 'success') {
            let shortNode = data.node.replace("http://", "").replace("127.0.0.1", "LOCALHOST");
            
            // UPDATED: Added inline style to DURATION value to match blue color
            resultArea.innerHTML = `
                <div class="result-card" style="width: 100%; grid-column: 1 / -1; padding: 2rem; border-color: var(--success);">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <span class="mono" style="color: var(--text-muted);">TARGET_MATCH_FOUND</span>
                    </div>
                    <div style="text-align: center; font-size: 3rem; font-family: var(--font-mono); font-weight: bold; color: var(--success); letter-spacing: 2px;">
                        ${data.pin}
                    </div>
                    <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem; font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">
                        <span>NODE: <span style="color: var(--accent);">${shortNode}</span></span>
                        <span>DURATION: <span style="color: var(--accent);">${data.time}</span></span>
                    </div>
                </div>
            `;
        } else {
            resultArea.innerHTML = `<div class="result-card" style="grid-column: 1/-1; color: var(--danger); text-align: center; padding: 2rem;">SEARCH_EXHAUSTED_NO_MATCH</div>`;
        }
    } catch (error) {
        resultArea.innerHTML = `<div class="result-card" style="grid-column: 1/-1; color: var(--danger);">CONNECTION_LOST</div>`;
    }
});

// --- LIVE TELEMETRY CHART ---

let cpuChart; 

function initChart() {
    const ctx = document.getElementById('cpuChart').getContext('2d');
    
    cpuChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], 
            datasets: [] 
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, 
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: '#333' },
                    ticks: { color: '#888' },
                    title: { display: true, text: 'CPU Usage %', color: '#555' }
                },
                x: {
                    grid: { display: false },
                    ticks: { display: false } 
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#ccc', font: { family: 'JetBrains Mono' } }
                }
            }
        }
    });
}

function updateTelemetry() {
    fetch('/grid_telemetry')
        .then(res => res.json())
        .then(workers => {
            if(!cpuChart) return;

            const now = new Date().toLocaleTimeString();

            if (cpuChart.data.labels.length > 20) {
                cpuChart.data.labels.shift();
            }
            cpuChart.data.labels.push(now);

            workers.forEach((worker, index) => {
                const nodeLabel = worker.node.replace("http://", "").replace("127.0.0.1", "NODE").replace("localhost", "NODE");
                
                let dataset = cpuChart.data.datasets.find(ds => ds.label === nodeLabel);
                
                if (!dataset) {
                    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
                    const color = colors[index % colors.length];

                    dataset = {
                        label: nodeLabel,
                        borderColor: color,
                        backgroundColor: color + '20', 
                        borderWidth: 2,
                        tension: 0.4, 
                        fill: true,
                        pointRadius: 0, 
                        pointHoverRadius: 4,
                        data: new Array(cpuChart.data.labels.length - 1).fill(0) 
                    };
                    cpuChart.data.datasets.push(dataset);
                }

                if (dataset.data.length > 20) {
                    dataset.data.shift();
                }
                
                dataset.data.push(worker.cpu);
            });

            cpuChart.update();
        });
}

initChart();
setInterval(updateTelemetry, 2000);