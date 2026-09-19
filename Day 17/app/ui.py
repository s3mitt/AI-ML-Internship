INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>RAG Document Q&A</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #4f46e5;
      --primary-hover: #4338ca;
      --primary-light: #eef2ff;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --success: #10b981;
      --danger: #ef4444;
      --radius: 12px;
      --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.07);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px 16px;
    }

    .container {
      max-width: 1000px;
      margin: 0 auto;
    }

    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      background: var(--card-bg);
      padding: 16px 24px;
      border-radius: var(--radius);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
    }

    .header-left h1 {
      font-size: 1.35rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #1e1b4b;
    }

    .badge {
      font-size: 0.75rem;
      padding: 2px 8px;
      border-radius: 9999px;
      font-weight: 600;
      background: var(--primary-light);
      color: var(--primary);
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .header-link {
      font-size: 0.875rem;
      color: var(--primary);
      text-decoration: none;
      font-weight: 500;
      padding: 6px 12px;
      border-radius: 6px;
      transition: background 0.15s;
    }

    .header-link:hover {
      background: var(--primary-light);
    }

    .grid {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 24px;
    }

    @media (max-width: 860px) {
      .grid {
        grid-template-columns: 1fr;
      }
    }

    .card {
      background: var(--card-bg);
      border-radius: var(--radius);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      padding: 20px;
      margin-bottom: 24px;
    }

    .card-title {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .upload-zone {
      border: 2px dashed var(--border);
      border-radius: 8px;
      padding: 24px 16px;
      text-align: center;
      cursor: pointer;
      background: #fafafa;
      transition: all 0.2s;
    }

    .upload-zone:hover, .upload-zone.dragover {
      border-color: var(--primary);
      background: var(--primary-light);
    }

    .upload-zone p {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 6px;
    }

    input[type="file"] {
      display: none;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: var(--primary);
      color: #ffffff;
      border: none;
      padding: 9px 16px;
      font-size: 0.875rem;
      font-weight: 500;
      border-radius: 6px;
      cursor: pointer;
      width: 100%;
      margin-top: 12px;
      transition: background 0.15s;
    }

    .btn:hover:not(:disabled) {
      background: var(--primary-hover);
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-sm {
      width: auto;
      padding: 4px 8px;
      font-size: 0.75rem;
      margin: 0;
    }

    .btn-danger {
      background: #fee2e2;
      color: var(--danger);
    }

    .btn-danger:hover:not(:disabled) {
      background: #fecaca;
    }

    .doc-list {
      list-style: none;
      max-height: 280px;
      overflow-y: auto;
    }

    .doc-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 12px;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 8px;
      font-size: 0.85rem;
    }

    .doc-info {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      margin-right: 8px;
    }

    .doc-name {
      font-weight: 600;
      color: var(--text);
    }

    .doc-meta {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .empty-state {
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
      padding: 20px 0;
    }

    .form-group {
      margin-bottom: 14px;
    }

    label {
      display: block;
      font-size: 0.85rem;
      font-weight: 500;
      margin-bottom: 6px;
      color: var(--text);
    }

    select, input[type="text"], textarea {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 9px 12px;
      font-family: inherit;
      font-size: 0.875rem;
      outline: none;
      transition: border-color 0.15s;
    }

    select:focus, input[type="text"]:focus, textarea:focus {
      border-color: var(--primary);
    }

    textarea {
      resize: vertical;
      min-height: 80px;
    }

    .alert {
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 0.85rem;
      margin-top: 10px;
      display: none;
    }

    .alert-success {
      background: #ecfdf5;
      color: #065f46;
      border: 1px solid #a7f3d0;
    }

    .alert-error {
      background: #fef2f2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }

    .answer-card {
      margin-top: 20px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fcfcfd;
      padding: 16px;
      display: none;
    }

    .answer-title {
      font-size: 0.9rem;
      font-weight: 600;
      margin-bottom: 8px;
      color: var(--primary);
    }

    .answer-body {
      font-size: 0.95rem;
      line-height: 1.6;
      white-space: pre-wrap;
      color: #1e293b;
    }

    .sources-title {
      margin-top: 16px;
      margin-bottom: 8px;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .chunk-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 10px 12px;
      margin-bottom: 8px;
      font-size: 0.825rem;
    }

    .chunk-header {
      display: flex;
      justify-content: space-between;
      color: var(--text-muted);
      font-size: 0.75rem;
      margin-bottom: 4px;
      font-family: 'JetBrains Mono', monospace;
    }

    .chunk-text {
      color: #334155;
      line-height: 1.45;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-left">
        <h1>Document Q&A <span class="badge">RAG API</span></h1>
      </div>
      <div class="header-right">
        <a href="/docs" target="_blank" class="header-link">Swagger Docs ↗</a>
        <a href="/health" target="_blank" class="header-link">Health Status ↗</a>
      </div>
    </header>

    <div class="grid">
      <div>
        <div class="card">
          <div class="card-title">Upload Document</div>
          <div class="upload-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" accept=".pdf,.docx,.txt" />
            <div style="font-size: 1.75rem; margin-bottom: 4px;">📄</div>
            <strong id="fileLabel">Choose file or drag here</strong>
            <p>Supported: PDF, DOCX, TXT (up to 20MB)</p>
          </div>
          <button class="btn" id="uploadBtn" onclick="handleUpload()" disabled>Upload & Index</button>
          <div id="uploadAlert" class="alert"></div>
        </div>

        <div class="card">
          <div class="card-title">
            <span>Indexed Documents</span>
            <button class="btn btn-sm" onclick="loadDocuments()" style="width: auto; background: var(--border); color: var(--text)">Refresh</button>
          </div>
          <ul class="doc-list" id="docList">
            <li class="empty-state">Loading documents...</li>
          </ul>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-title">Ask a Question</div>
          <div class="form-group">
            <label for="docSelect">Scope to Document (Optional)</label>
            <select id="docSelect">
              <option value="">All Uploaded Documents</option>
            </select>
          </div>

          <div class="form-group">
            <label for="questionInput">Question</label>
            <textarea id="questionInput" placeholder="Ask anything about the contents of the uploaded document(s)..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();handleAsk();}"></textarea>
          </div>

          <div style="display: flex; gap: 12px; align-items: flex-end;">
            <div class="form-group" style="width: 110px; margin-bottom: 0;">
              <label for="topK">Top Chunks</label>
              <select id="topK">
                <option value="2">2</option>
                <option value="4" selected>4</option>
                <option value="6">6</option>
                <option value="8">8</option>
              </select>
            </div>
            <button class="btn" id="askBtn" onclick="handleAsk()" style="flex: 1; margin-top: 0; height: 42px;">Ask Question</button>
          </div>

          <div id="askAlert" class="alert"></div>

          <div id="answerCard" class="answer-card">
            <div class="answer-title">Answer</div>
            <div class="answer-body" id="answerBody"></div>
            
            <div class="sources-title">Retrieved Chunks & Citations</div>
            <div id="sourcesList"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let selectedFile = null;

    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const fileLabel = document.getElementById('fileLabel');
    const uploadBtn = document.getElementById('uploadBtn');

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        fileLabel.textContent = selectedFile.name + " (" + (selectedFile.size / 1024).toFixed(1) + " KB)";
        uploadBtn.disabled = false;
      }
    });

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        selectedFile = e.dataTransfer.files[0];
        fileLabel.textContent = selectedFile.name + " (" + (selectedFile.size / 1024).toFixed(1) + " KB)";
        uploadBtn.disabled = false;
      }
    });

    function showAlert(elementId, message, type) {
      const el = document.getElementById(elementId);
      el.textContent = message;
      el.className = 'alert alert-' + type;
      el.style.display = 'block';
    }

    function hideAlert(elementId) {
      const el = document.getElementById(elementId);
      el.style.display = 'none';
    }

    async function handleUpload() {
      if (!selectedFile) return;
      uploadBtn.disabled = true;
      uploadBtn.textContent = "Processing & Indexing...";
      hideAlert('uploadAlert');

      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const res = await fetch('/upload', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (res.ok) {
          showAlert('uploadAlert', `Indexed "${data.document.filename}" into ${data.document.num_chunks} chunks!`, 'success');
          fileInput.value = '';
          fileLabel.textContent = 'Choose file or drag here';
          selectedFile = null;
          loadDocuments();
        } else {
          showAlert('uploadAlert', data.detail || 'Upload failed.', 'error');
        }
      } catch (err) {
        showAlert('uploadAlert', 'Connection error: ' + err.message, 'error');
      } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload & Index";
      }
    }

    async function loadDocuments() {
      const listEl = document.getElementById('docList');
      const selectEl = document.getElementById('docSelect');

      try {
        const res = await fetch('/documents');
        const docs = await res.json();

        if (!docs || docs.length === 0) {
          listEl.innerHTML = '<li class="empty-state">No documents uploaded yet.</li>';
          selectEl.innerHTML = '<option value="">All Uploaded Documents</option>';
          return;
        }

        listEl.innerHTML = docs.map(d => `
          <li class="doc-item">
            <div class="doc-info" title="${d.filename}">
              <div class="doc-name">${d.filename}</div>
              <div class="doc-meta">${d.num_chunks} chunks • ${(d.file_size_bytes/1024).toFixed(1)} KB</div>
            </div>
            <button class="btn btn-sm btn-danger" onclick="deleteDoc('${d.doc_id}')">Delete</button>
          </li>
        `).join('');

        const currentVal = selectEl.value;
        selectEl.innerHTML = '<option value="">All Uploaded Documents</option>' +
          docs.map(d => `<option value="${d.doc_id}">${d.filename}</option>`).join('');
        if (currentVal) selectEl.value = currentVal;
      } catch (err) {
        listEl.innerHTML = '<li class="empty-state" style="color:var(--danger)">Failed to load documents.</li>';
      }
    }

    async function deleteDoc(docId) {
      if (!confirm('Are you sure you want to delete this document?')) return;
      try {
        const res = await fetch(`/documents/${docId}`, { method: 'DELETE' });
        if (res.ok) {
          loadDocuments();
        } else {
          const data = await res.json();
          alert(data.detail || 'Failed to delete.');
        }
      } catch (err) {
        alert('Network error: ' + err.message);
      }
    }

    async function handleAsk() {
      const qInput = document.getElementById('questionInput');
      const question = qInput.value.trim();
      if (!question) return;

      const docId = document.getElementById('docSelect').value || null;
      const topK = parseInt(document.getElementById('topK').value, 10) || 4;
      const askBtn = document.getElementById('askBtn');
      const answerCard = document.getElementById('answerCard');
      const answerBody = document.getElementById('answerBody');
      const sourcesList = document.getElementById('sourcesList');

      hideAlert('askAlert');
      askBtn.disabled = true;
      askBtn.textContent = 'Searching...';

      try {
        const res = await fetch('/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, doc_id: docId, top_k: topK })
        });
        const data = await res.json();
        if (res.ok) {
          answerBody.textContent = data.answer;
          sourcesList.innerHTML = data.sources.map((s, idx) => `
            <div class="chunk-card">
              <div class="chunk-header">
                <span>#${idx + 1} • Doc: ${s.doc_id.substring(0, 8)}... (Chunk ${s.chunk_index})</span>
                <span>Score: ${(s.score).toFixed(3)}</span>
              </div>
              <div class="chunk-text">${s.text}</div>
            </div>
          `).join('');
          answerCard.style.display = 'block';
        } else {
          showAlert('askAlert', data.detail || 'Failed to get an answer.', 'error');
          answerCard.style.display = 'none';
        }
      } catch (err) {
        showAlert('askAlert', 'Network error: ' + err.message, 'error');
        answerCard.style.display = 'none';
      } finally {
        askBtn.disabled = false;
        askBtn.textContent = 'Ask Question';
      }
    }

    loadDocuments();
  </script>
</body>
</html>
"""
