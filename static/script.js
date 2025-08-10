const messages = document.getElementById('messages');
const questionInput = document.getElementById('questionInput');
const askBtn = document.getElementById('askBtn');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const pasteText = document.getElementById('pasteText');
const sourceName = document.getElementById('sourceName');
const addTextBtn = document.getElementById('addTextBtn');
const chunkCount = document.getElementById('chunkCount');

let chatHistory = [];
let hasMessages = false;

// load stats
updateStats();

// file upload
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', (e) => { e.preventDefault(); dropZone.classList.remove('dragover'); if (e.dataTransfer.files[0]) uploadFile(e.dataTransfer.files[0]); });
fileInput.addEventListener('change', (e) => { if (e.target.files[0]) uploadFile(e.target.files[0]); });

async function uploadFile(file) {
    dropZone.innerHTML = '<p>Uploading...</p>';
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_name', file.name);

    try {
        const res = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        dropZone.innerHTML = '<p>📎 Drop PDF/TXT here</p>';
        addNotice(data.message);
        updateStats();
    } catch (err) {
        dropZone.innerHTML = `<p style="color:#f87171">${err.message}</p>`;
        setTimeout(() => { dropZone.innerHTML = '<p>📎 Drop PDF/TXT here</p>'; }, 3000);
    }
}

// add text
addTextBtn.addEventListener('click', async () => {
    const text = pasteText.value.trim();
    if (!text) return;
    addTextBtn.textContent = 'Adding...';
    try {
        const res = await fetch('/api/add-text', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, source_name: sourceName.value || 'Pasted Text' })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        pasteText.value = ''; sourceName.value = '';
        addNotice(data.message);
        updateStats();
    } catch (err) { alert(err.message); }
    addTextBtn.textContent = 'Add Text';
});

// ask question
askBtn.addEventListener('click', ask);
questionInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') ask(); });

async function ask() {
    const q = questionInput.value.trim();
    if (!q) return;

    if (!hasMessages) { messages.innerHTML = ''; hasMessages = true; }

    addMessage('user', q);
    chatHistory.push({ role: 'user', content: q });
    questionInput.value = '';
    askBtn.disabled = true;
    askBtn.textContent = '...';

    try {
        const res = await fetch('/api/ask', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: q, chat_history: chatHistory })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        addMessage('assistant', data.answer, data.sources);
        chatHistory.push({ role: 'assistant', content: data.answer });
    } catch (err) {
        addMessage('assistant', `Error: ${err.message}`);
    }

    askBtn.disabled = false;
    askBtn.textContent = 'Ask';
    questionInput.focus();
}

function addMessage(role, content, sources = []) {
    const div = document.createElement('div');
    div.className = `msg ${role}`;

    let html = role === 'user' ? escapeHtml(content) : marked.parse(content);

    if (sources && sources.length > 0) {
        html += '<div class="sources"><div class="sources-title">Sources used:</div>';
        sources.forEach(s => { html += `<span class="source-chip">${escapeHtml(s.source)} (${s.score}%)</span>`; });
        html += '</div>';
    }

    div.innerHTML = html;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function addNotice(text) {
    if (!hasMessages) { messages.innerHTML = ''; hasMessages = true; }
    const div = document.createElement('div');
    div.className = 'upload-notice';
    div.textContent = '✅ ' + text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

async function updateStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        chunkCount.textContent = data.total_chunks;
    } catch {}
}

function escapeHtml(t) { return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
