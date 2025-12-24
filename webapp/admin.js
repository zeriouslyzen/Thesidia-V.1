// Katanx Matrix 2.0 - Feature-Packed Dashboard

let currentView = 'nexus';
let globe = null;
let memoryGaugeChart = null;
let neuralVelocityChart = null;
let velocityData = [];
const MAX_VELOCITY_POINTS = 20;

// ========================================
// Storage Keys
// ========================================
const STORAGE = {
    TASKS: 'matrix_tasks',
    NOTES: 'matrix_notes',
    CHAT: 'matrix_chat',
    VAULT: 'matrix_vault',
    WIDGETS: 'matrix_widgets'
};

// ========================================
// Navigation
// ========================================
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        if (view) loadView(view);
    });
});

function loadView(viewName) {
    currentView = viewName;
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll(`.nav-btn[data-view="${viewName}"]`).forEach(b => b.classList.add('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`view-${viewName}`)?.classList.add('active');

    const titles = {
        'nexus': 'Nexus',
        'cerebro': 'Cerebro',
        'oracle': 'Oracle AI',
        'vault': 'Neural Vault',
        'feeds': 'Feeds',
        'marketing': 'Marketing Forge',
        'settings': 'Settings'
    };
    document.getElementById('view-title').textContent = titles[viewName] || viewName;

    lucide.createIcons();
    if (viewName === 'nexus') { refreshNeuralStatus(); initGlobe(); }
    if (viewName === 'marketing') loadActivity();
    if (viewName === 'cerebro') loadModelInventory();
    if (viewName === 'settings') renderWidgetToggles();
}

// ========================================
// Neural Status
// ========================================
async function refreshNeuralStatus() {
    try {
        const res = await fetch('/api/neural/status');
        if (!res.ok) return;
        const data = await res.json();
        const model = data.active_model || 'None';
        document.getElementById('m-model').textContent = model.split(':')[0] || model;
        document.getElementById('m-memory').textContent = `${data.memory.percent}%`;
        document.getElementById('m-loaded').textContent = data.loaded_models.length;
        const uptime = Math.floor(data.uptime_seconds);
        document.getElementById('m-uptime').textContent = `${Math.floor(uptime / 3600)}h ${Math.floor((uptime % 3600) / 60)}m`;

        // Update charts
        updateCharts(data.memory.percent);
    } catch (e) { console.error('[Matrix] Neural status error:', e); }
}

// ========================================
// Calendar
// ========================================
function renderCalendar() {
    const container = document.getElementById('calendar-week');
    if (!container) return;
    container.innerHTML = '';
    const today = new Date();
    const dayOfWeek = today.getDay();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - dayOfWeek);

    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    for (let i = 0; i < 7; i++) {
        const d = new Date(startOfWeek);
        d.setDate(startOfWeek.getDate() + i);
        const isToday = d.toDateString() === today.toDateString();
        container.innerHTML += `
            <div class="calendar-day ${isToday ? 'today' : ''}" onclick="selectDay(${d.getDate()})">
                <div class="day-name">${days[i]}</div>
                <div class="day-num">${d.getDate()}</div>
            </div>`;
    }
}

function selectDay(day) { console.log('[Matrix] Selected day:', day); }

// ========================================
// Charts
// ========================================
function initMemoryGauge() {
    const canvas = document.getElementById('memory-gauge-chart');
    if (!canvas || memoryGaugeChart) return;
    const ctx = canvas.getContext('2d');
    memoryGaugeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: [
                    'rgba(88, 166, 255, 0.8)',
                    'rgba(255, 255, 255, 0.05)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '75%',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    });
}

function initNeuralVelocityChart() {
    const canvas = document.getElementById('neural-velocity-chart');
    if (!canvas || neuralVelocityChart) return;
    const ctx = canvas.getContext('2d');
    neuralVelocityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Memory %',
                data: [],
                borderColor: 'rgba(88, 166, 255, 0.8)',
                backgroundColor: 'rgba(88, 166, 255, 0.1)',
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            scales: {
                x: { display: false },
                y: {
                    display: true,
                    min: 0,
                    max: 100,
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.3)',
                        font: { size: 8 }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                }
            },
            animation: {
                duration: 750
            }
        }
    });
}

function updateCharts(memoryPercent) {
    // Update memory gauge
    if (memoryGaugeChart) {
        memoryGaugeChart.data.datasets[0].data = [memoryPercent, 100 - memoryPercent];
        memoryGaugeChart.update('none');
    }

    // Update velocity chart
    if (neuralVelocityChart) {
        velocityData.push(memoryPercent);
        if (velocityData.length > MAX_VELOCITY_POINTS) velocityData.shift();
        neuralVelocityChart.data.labels = velocityData.map((_, i) => i);
        neuralVelocityChart.data.datasets[0].data = velocityData;
        neuralVelocityChart.update('none');
    }
}
function initGlobe() {
    const container = document.getElementById('globe-container');
    if (!container || globe) return;
    try {
        const metrologyData = [
            { lat: 37.7749, lng: -122.4194, size: 0.6, label: 'INTEL-01', freq: '432Hz', color: '#58a6ff' },
            { lat: 51.5074, lng: -0.1278, size: 0.4, label: 'NEURAL-04', freq: '528Hz', color: '#3fb950' },
            { lat: 35.6762, lng: 139.6503, size: 0.7, label: 'ID-OMEGA', freq: '639Hz', color: '#d29922' },
            { lat: -33.8688, lng: 151.2093, size: 0.3, label: 'SYST-09', freq: '741Hz', color: '#a371f7' },
            { lat: 0, lng: 0, size: 0.5, label: 'VOID-ZERO', freq: '852Hz', color: '#f85149' },
            { lat: 40.7128, lng: -74.0060, size: 0.45, label: 'CORE-NYC', freq: '963Hz', color: '#58a6ff' }
        ];

        const width = container.clientWidth || 250;
        const height = container.clientHeight || 210;

        globe = Globe()(container)
            .width(width)
            .height(height)
            .globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg')
            .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
            .backgroundColor('rgba(0,0,0,0)')
            .pointsData(metrologyData)
            .pointAltitude('size')
            .pointColor('color')
            .pointRadius(0.6)
            .labelsData(metrologyData)
            .labelText(d => `${d.label}\n${d.freq}`)
            .labelSize(1.5)
            .labelDotRadius(0.2)
            .labelColor('color')
            .labelResolution(2)
            .pointsTransitionDuration(1000);

        globe.controls().autoRotate = true;
        globe.controls().autoRotateSpeed = 0.5;
        globe.controls().enableZoom = false;

        // Visual enhancement: Improved brightness and atmosphere
        const globeMaterial = globe.globeMaterial();
        globeMaterial.color.set('#1a2a4b');
        globeMaterial.emissive.set('#0a1a3a');
        globeMaterial.emissiveIntensity = 0.5;
        globeMaterial.shininess = 0.8;

    } catch (e) { console.error('[Matrix] Cosmic Globe error:', e); }
}

// ========================================
// Team Chat & Board
// ========================================
function toggleSlidingChat() {
    const chat = document.getElementById('sliding-chat');
    if (chat) chat.classList.toggle('open');
}

function loadChat() {
    const messages = JSON.parse(localStorage.getItem(STORAGE.CHAT) || '[]');

    // 1. Sliding Chat (Active Communication)
    const chatContainer = document.getElementById('chat-messages');
    if (chatContainer) {
        chatContainer.innerHTML = messages.map(m => `
            <div class="chat-msg">
                <span class="sender">${m.sender}</span>${m.text}
                <span class="time">${m.time}</span>
            </div>
        `).join('');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // 2. Universal Board (Important Posts Only)
    const boardContainer = document.getElementById('board-messages');
    if (boardContainer) {
        // For now, filter messages starting with "!" or show last 5
        const important = messages.filter(m => m.text.startsWith('!')).slice(-5);
        if (important.length === 0) {
            boardContainer.innerHTML = '<div style="color:var(--text-dim); text-align:center; padding:10px;">Waiting for critical updates...</div>';
        } else {
            boardContainer.innerHTML = important.map(m => `
                <div class="chat-msg" style="border-left: 2px solid var(-- gold);">
                    <span class="sender" style="color:var(--gold)">BOARD</span>${m.text.substring(1)}
                    <span class="time">${m.time}</span>
                </div>
            `).join('');
        }
    }
}

function sendChat() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;
    const messages = JSON.parse(localStorage.getItem(STORAGE.CHAT) || '[]');
    messages.push({ sender: 'You', text, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });
    if (messages.length > 50) messages.shift();
    localStorage.setItem(STORAGE.CHAT, JSON.stringify(messages));
    input.value = '';
    loadChat();
    addActivity('Sent chat message');
}

function uploadFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = e => {
        const file = e.target.files[0];
        if (file) {
            const messages = JSON.parse(localStorage.getItem(STORAGE.CHAT) || '[]');
            messages.push({ sender: 'You', text: `[File: ${file.name}]`, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });
            localStorage.setItem(STORAGE.CHAT, JSON.stringify(messages));
            loadChat();
            addActivity(`Uploaded: ${file.name}`);
        }
    };
    input.click();
}

// ========================================
// Marketing Forge
// ========================================
function uploadAsset() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,video/*';
    input.onchange = e => {
        const file = e.target.files[0];
        if (file) {
            const gallery = document.getElementById('asset-gallery');
            const item = document.createElement('div');
            item.className = 'data-item';
            item.style.padding = '2px';
            item.style.height = '60px';
            item.style.display = 'flex';
            item.style.alignItems = 'center';
            item.style.justifyContent = 'center';
            item.innerHTML = `<span style="font-size:8px; overflow:hidden; text-overflow:ellipsis;">${file.name}</span>`;
            if (gallery) gallery.appendChild(item);
            addActivity(`Asset Synced: ${file.name}`);
        }
    };
    input.click();
}

function executeProcedure(id) {
    addActivity(`Executing AI Procedure: ${id}`);
    const board = document.getElementById('board-messages');
    if (board) {
        const msg = {
            sender: 'SYSTEM',
            text: `!PROCEDURE ${id} INITIATED - TARGETING ALL NODES`,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        const messages = JSON.parse(localStorage.getItem(STORAGE.CHAT) || '[]');
        messages.push(msg);
        localStorage.setItem(STORAGE.CHAT, JSON.stringify(messages));
        loadChat();
    }
}

function loadTasks() {
    const tasks = JSON.parse(localStorage.getItem(STORAGE.TASKS) || '[]');
    const container = document.getElementById('task-list');
    if (!container) return;
    container.innerHTML = tasks.map((t, i) => `
        <div class="task-item">
            <div class="task-checkbox ${t.done ? 'checked' : ''}" onclick="toggleTask(${i})">
                ${t.done ? '<i data-lucide="check" style="width:10px;height:10px;"></i>' : ''}
            </div>
            <span class="task-text ${t.done ? 'done' : ''}">${t.text}</span>
        </div>
    `).join('');
    lucide.createIcons();
}

function addTask() {
    const input = document.getElementById('new-task');
    const text = input.value.trim();
    if (!text) return;
    const tasks = JSON.parse(localStorage.getItem(STORAGE.TASKS) || '[]');
    tasks.push({ text, done: false });
    localStorage.setItem(STORAGE.TASKS, JSON.stringify(tasks));
    input.value = '';
    loadTasks();
    addActivity(`Added task: ${text}`);
}

function toggleTask(index) {
    const tasks = JSON.parse(localStorage.getItem(STORAGE.TASKS) || '[]');
    if (tasks[index]) {
        tasks[index].done = !tasks[index].done;
        localStorage.setItem(STORAGE.TASKS, JSON.stringify(tasks));
        loadTasks();
    }
}

// ========================================
// Quick Notes
// ========================================
function loadNotes() {
    const notes = localStorage.getItem(STORAGE.NOTES) || '';
    const editor = document.getElementById('quick-notes');
    if (editor) editor.value = notes;
}

document.getElementById('quick-notes')?.addEventListener('input', e => {
    localStorage.setItem(STORAGE.NOTES, e.target.value);
});

// ========================================
// Activity Feed
// ========================================
function loadActivity() {
    const activities = JSON.parse(localStorage.getItem('matrix_activity') || '[]');
    const container = document.getElementById('activity-feed');
    if (!container) return;
    container.innerHTML = activities.slice(-10).reverse().map(a => `
        <div class="activity-item">
            <span class="activity-icon"><i data-lucide="circle" style="width:8px;height:8px;"></i></span>
            <span>${a.text}</span>
            <span class="activity-time">${a.time}</span>
        </div>
    `).join('');
    lucide.createIcons();
}

function addActivity(text) {
    const activities = JSON.parse(localStorage.getItem('matrix_activity') || '[]');
    activities.push({ text, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });
    if (activities.length > 50) activities.shift();
    localStorage.setItem('matrix_activity', JSON.stringify(activities));
    loadActivity();
}

// ========================================
// Neural Vault
// ========================================
function saveVaultNote() {
    const content = document.getElementById('vault-editor')?.value || '';
    localStorage.setItem(STORAGE.VAULT, content);
    addActivity('Saved vault note');
}

function loadVaultNotes() {
    const content = localStorage.getItem(STORAGE.VAULT) || '';
    const editor = document.getElementById('vault-editor');
    if (editor) editor.value = content;
}

// ========================================
// Model Inventory
// ========================================
async function loadModelInventory() {
    try {
        const res = await fetch('/api/neural/status');
        if (!res.ok) return;
        const data = await res.json();
        const container = document.getElementById('model-list');
        container.innerHTML = data.available_models.map(m => {
            const isActive = data.active_model === m;
            const isLoaded = data.loaded_models.includes(m);
            return `<div class="data-item">
                <span class="label">${m}</span>
                <span class="value">${isActive ? '<span style="color:var(--green)">Active</span>' : isLoaded ? '<span style="color:var(--gold)">Loaded</span>' : '<button class="btn" onclick="loadModel(\'' + m + '\')">Load</button>'}</span>
            </div>`;
        }).join('');
    } catch (e) { document.getElementById('model-list').innerHTML = '<div style="color:var(--red)">Error</div>'; }
}

async function loadModel(name) {
    await fetch('/api/neural/load', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ model: name }) });
    loadModelInventory();
    addActivity(`Loaded model: ${name}`);
}

// ========================================
// Oracle AI
// ========================================
async function sendQuery() {
    const input = document.getElementById('ai-input');
    const output = document.getElementById('ai-output');
    const query = input.value.trim();
    if (!query) return;
    input.value = '';
    output.textContent = 'Processing...';
    try {
        const res = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: query, task_type: 'conversation' }) });
        if (!res.ok) throw new Error('API error');
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        output.textContent = '';
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            output.textContent += decoder.decode(value);
        }
        addActivity('AI query completed');
    } catch (e) { output.textContent = 'Error: ' + e.message; }
}

// ========================================
// Widget Toggles
// ========================================
const WIDGET_NAMES = ['metrics', 'calendar', 'globe', 'chat', 'tasks', 'notes', 'activity'];

function getWidgetSettings() {
    return JSON.parse(localStorage.getItem(STORAGE.WIDGETS) || '{}');
}

function renderWidgetToggles() {
    const settings = getWidgetSettings();
    const container = document.getElementById('widget-toggles');
    if (!container) return;
    container.innerHTML = WIDGET_NAMES.map(w => `
        <div class="data-item">
            <span class="label">${w.charAt(0).toUpperCase() + w.slice(1)}</span>
            <span class="value">
                <input type="checkbox" ${settings[w] !== false ? 'checked' : ''} onchange="toggleWidget('${w}', this.checked)">
            </span>
        </div>
    `).join('');
}

function toggleWidget(name, enabled) {
    const settings = getWidgetSettings();
    settings[name] = enabled;
    localStorage.setItem(STORAGE.WIDGETS, JSON.stringify(settings));
    applyWidgetSettings();
}

function applyWidgetSettings() {
    const settings = getWidgetSettings();
    document.querySelectorAll('[data-widget]').forEach(el => {
        const name = el.dataset.widget;
        el.classList.toggle('disabled', settings[name] === false);
    });
}

// ========================================
// Command Palette
// ========================================
const COMMANDS = [
    { name: 'Go to Nexus', icon: 'layout-dashboard', action: () => loadView('nexus') },
    { name: 'Go to Cerebro', icon: 'brain', action: () => loadView('cerebro') },
    { name: 'Go to Oracle AI', icon: 'sparkles', action: () => loadView('oracle') },
    { name: 'Go to Vault', icon: 'file-text', action: () => loadView('vault') },
    { name: 'Go to Settings', icon: 'settings', action: () => loadView('settings') },
    { name: 'Refresh Data', icon: 'refresh-cw', action: () => { refreshNeuralStatus(); addActivity('Refreshed data'); } },
];

function openCommandPalette() {
    document.getElementById('overlay').classList.add('open');
    document.getElementById('command-palette').classList.add('open');
    document.getElementById('command-input').value = '';
    document.getElementById('command-input').focus();
    filterCommands('');
}

function closeCommandPalette() {
    document.getElementById('overlay').classList.remove('open');
    document.getElementById('command-palette').classList.remove('open');
}

function filterCommands(query) {
    const filtered = COMMANDS.filter(c => c.name.toLowerCase().includes(query.toLowerCase()));
    document.getElementById('command-results').innerHTML = filtered.map((c, i) => `
        <div class="command-item" onclick="executeCommand(${i})">
            <i data-lucide="${c.icon}"></i>
            <span>${c.name}</span>
        </div>
    `).join('');
    lucide.createIcons();
}

function executeCommand(index) {
    COMMANDS[index]?.action();
    closeCommandPalette();
}

document.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        openCommandPalette();
    }
    if (e.key === 'Escape') closeCommandPalette();
});

// ========================================
// Boot
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Matrix 2.0] Initializing...');
    refreshNeuralStatus();
    renderCalendar();
    loadChat();
    loadTasks();
    loadNotes();
    loadActivity();
    loadVaultNotes();
    applyWidgetSettings();
    setTimeout(initGlobe, 500);
    setTimeout(initMemoryGauge, 500);
    setTimeout(initNeuralVelocityChart, 500);
    setInterval(() => { if (currentView === 'nexus') refreshNeuralStatus(); }, 3000);
});
