/**
 * Core Editor Logic
 * Handles state, rendering, and API communication.
 */

document.addEventListener('DOMContentLoaded', () => {
    const config = window.EDITOR_CONFIG || {};
    const toolConfig = TOOLS[config.tool];
    
    if (!toolConfig) {
        console.error("Unknown tool:", config.tool);
        displayStatus("Error: Unknown tool configuration", "error");
        return;
    }

    // 1. Initialize UI
    renderLeftPanel(toolConfig.leftPanel);
    renderRightPanel(toolConfig.rightPanel);
    renderCanvas(config.files, toolConfig.canvasMode);
    
    // 2. Event Listeners
    setupGlobalEvents();
    
    // 3. Setup Upload if present
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
});

function renderLeftPanel(items) {
    const container = document.getElementById('leftPanel');
    container.innerHTML = '';
    
    if (!items || items.length === 0) return;

    items.forEach(item => {
        if (item.type === 'separator') {
            const sep = document.createElement('div');
            sep.className = 'tool-separator';
            sep.style.cssText = 'width: 80%; height: 1px; background: var(--border); margin: 10px 0;';
            container.appendChild(sep);
            return;
        }
        
        const btn = document.createElement('div');
        btn.className = 'tool-icon';
        btn.innerHTML = item.icon;
        btn.title = item.title;
        btn.dataset.tool = item.id; // For active state
        btn.onclick = () => handleToolAction(item.id, item.tool);
        container.appendChild(btn);
    });
}

function renderCanvas(files, mode) {
    const container = document.getElementById('canvasContent');
    const uploadContainer = document.getElementById('uploadContainer');

    // If no files, show upload box (handled by template usually, but we check here)
    if (!files || files.length === 0) {
        if (!uploadContainer) {
            // Re-inject upload box if missing (e.g. after deleting last file)
            container.innerHTML = `
                <div class="placeholder-msg" id="uploadContainer">
                    <div class="upload-box" id="dropZone">
                        <div class="upload-icon">📄</div>
                        <h2>Select PDF files</h2>
                        <input type="file" id="fileInput" multiple style="display:none">
                        <button class="btn-primary" onclick="document.getElementById('fileInput').click()">Select Files</button>
                    </div>
                </div>`;
            document.getElementById('fileInput').addEventListener('change', handleFileUpload);
        }
        return;
    }

    // Clear placeholder
    container.innerHTML = '';

    if (mode === 'grid') {
        renderGridView(container, files);
    } else if (mode === 'pages') {
        renderPageGridView(container, files);
    } else if (mode === 'advanced') {
        renderAdvancedEditorView(container, files);
    } else {
        const iframe = document.createElement('iframe');
        iframe.src = files[0].url + "#toolbar=0";
        iframe.className = 'pdf-viewer-frame';
        container.appendChild(iframe);
    }
}

/**
 * Advanced Editor View - PDF with Fabric.js overlay
 */
async function renderAdvancedEditorView(container, files) {
    if (!files || files.length === 0) return;
    const file = files[0];
    
    // Create wrapper for PDF + overlay
    const wrapper = document.createElement('div');
    wrapper.id = 'advanced-editor-wrapper';
    wrapper.style.cssText = 'position: relative; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; overflow: auto;';
    container.appendChild(wrapper);
    
    displayStatus("Loading PDF...", "normal");
    
    try {
        const loadingTask = pdfjsLib.getDocument(file.url);
        const pdf = await loadingTask.promise;
        
        window.EDITOR_CONFIG.pdfDoc = pdf;
        window.EDITOR_CONFIG.pageCount = pdf.numPages;
        window.EDITOR_STATE = window.EDITOR_STATE || {};
        window.EDITOR_STATE.currentPage = 1;
        
        // Render first page as canvas
        const pageContainer = document.createElement('div');
        pageContainer.id = 'page-container';
        pageContainer.style.cssText = 'position: relative; margin: 20px auto; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
        wrapper.appendChild(pageContainer);
        
        await renderPDFPage(pdf, 1, pageContainer);
        
        // Initialize Fabric.js overlay on top
        setTimeout(() => {
            if (typeof initFabricOverlay === 'function') {
                initFabricOverlay('#page-container');
            }
            displayStatus(`Loaded ${pdf.numPages} page(s). Select a tool to edit.`, "success");
        }, 100);
        
        // Add page navigation if multiple pages
        if (pdf.numPages > 1) {
            const nav = document.createElement('div');
            nav.id = 'page-nav';
            nav.style.cssText = 'display: flex; gap: 12px; align-items: center; margin-top: 16px;';
            nav.innerHTML = `
                <button class="btn-secondary" onclick="navigatePage(-1)">◀ Prev</button>
                <span id="page-indicator" style="font-size: 0.9rem; color: var(--gray);">Page 1 of ${pdf.numPages}</span>
                <button class="btn-secondary" onclick="navigatePage(1)">Next ▶</button>
            `;
            wrapper.appendChild(nav);
        }
        
    } catch(err) {
        console.error("Error loading PDF:", err);
        displayStatus("Error loading PDF", "error");
    }
}

/**
 * Render a single PDF page to canvas
 */
async function renderPDFPage(pdf, pageNum, container) {
    const page = await pdf.getPage(pageNum);
    
    // Clear previous
    container.innerHTML = '';
    
    // Calculate scale based on container width
    const containerWidth = document.getElementById('mainCanvas').clientWidth - 80;
    const unscaledViewport = page.getViewport({ scale: 1 });
    const scale = Math.min(containerWidth / unscaledViewport.width, 1.5);
    const viewport = page.getViewport({ scale: scale });
    
    // Create canvas for PDF
    const pdfCanvas = document.createElement('canvas');
    pdfCanvas.id = 'pdf-page-canvas';
    pdfCanvas.width = viewport.width;
    pdfCanvas.height = viewport.height;
    container.style.width = viewport.width + 'px';
    container.style.height = viewport.height + 'px';
    container.appendChild(pdfCanvas);
    
    const ctx = pdfCanvas.getContext('2d');
    await page.render({ canvasContext: ctx, viewport: viewport }).promise;
}

/**
 * Navigate between pages
 */
async function navigatePage(delta) {
    const pdf = window.EDITOR_CONFIG.pdfDoc;
    if (!pdf) return;
    
    let newPage = window.EDITOR_STATE.currentPage + delta;
    newPage = Math.max(1, Math.min(newPage, pdf.numPages));
    
    if (newPage !== window.EDITOR_STATE.currentPage) {
        window.EDITOR_STATE.currentPage = newPage;
        
        const pageContainer = document.getElementById('page-container');
        await renderPDFPage(pdf, newPage, pageContainer);
        
        // Reinitialize Fabric overlay
        setTimeout(() => {
            if (typeof initFabricOverlay === 'function') {
                initFabricOverlay('#page-container');
            }
        }, 100);
        
        // Update indicator
        const indicator = document.getElementById('page-indicator');
        if (indicator) {
            indicator.innerText = `Page ${newPage} of ${pdf.numPages}`;
        }
    }
}

async function renderPageGridView(container, files) {
    // For Edit PDF, we assume working on the FIRST file initially
    if (!files || files.length === 0) return;
    const file = files[0];

    const grid = document.createElement('div');
    grid.className = 'file-grid';
    grid.id = 'pageGrid';
    container.appendChild(grid);

    displayStatus("Loading pages...", "normal");

    try {
        const loadingTask = pdfjsLib.getDocument(file.url);
        const pdf = await loadingTask.promise;
        
        window.EDITOR_CONFIG.pageCount = pdf.numPages;
        window.EDITOR_CONFIG.currentPageConfig = []; // To track rotations/deletions

        for (let i = 1; i <= pdf.numPages; i++) {
            const card = document.createElement('div');
            card.className = 'file-card';
            card.dataset.pageNum = i;
            // No drag-drop for pages yet, maybe later
            
            const canvasId = `page-thumb-${i}`;
            
            card.innerHTML = `
                <div class="file-preview-wrapper">
                    <canvas id="${canvasId}" class="pdf-thumb"></canvas>
                    <div class="page-number-overlay" style="position: absolute; bottom: 5px; right: 5px; background: rgba(0,0,0,0.6); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem;">${i}</div>
                </div>
                <div class="card-actions" style="opacity: 1; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 100%; justify-content: center;">
                    <button class="btn-mini" onclick="rotatePage(${i}, -90)" title="Rotate Left">↺</button>
                    <button class="btn-mini" onclick="rotatePage(${i}, 90)" title="Rotate Right">↻</button>
                    <button class="btn-mini btn-danger" onclick="deletePage(${i})" title="Delete">🗑️</button>
                </div>
            `;
            
            grid.appendChild(card);
            
            // Render specific page
            renderPageThumbnail(pdf, i, canvasId);
        }
        displayStatus(`Loaded ${pdf.numPages} pages.`, "success");

    } catch(err) {
        console.error("Error loading PDF pages:", err);
        displayStatus("Error loading pages.", "error");
    }
}

async function renderPageThumbnail(pdf, pageNum, canvasId) {
    try {
        const page = await pdf.getPage(pageNum);
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const wrapper = canvas.parentElement;
        const targetWidth = wrapper.clientWidth || 150;
        const unscaledViewport = page.getViewport({scale: 1});
        const scale = (targetWidth / unscaledViewport.width) * 1.5;
        const viewport = page.getViewport({scale: scale});

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        await page.render({
            canvasContext: canvas.getContext('2d'),
            viewport: viewport
        }).promise;
    } catch(e) {
        console.error(e);
    }
}

function renderGridView(container, files) {
    const grid = document.createElement('div');
    grid.className = 'file-grid';
    
    files.forEach((file, index) => {
        const card = document.createElement('div');
        card.className = 'file-card';
        card.draggable = true;
        card.dataset.index = index;
        
        // IDs
        const canvasId = `thumb-${index}`;
        const pageCountId = `pages-${index}`;
        const metaId = `meta-${index}`; // For size/pages
        
        card.innerHTML = `
            <div class="file-preview-wrapper" id="wrapper-${index}">
                <canvas id="${canvasId}" class="pdf-thumb"></canvas>
                <div id="loader-${index}" style="font-size:0.8rem; color:#999; position:absolute;">Loading...</div>
            </div>
            <div class="file-info-grid">
                <div class="file-name" title="${file.name}">${file.name}</div>
                <div class="file-meta-row">
                    <span class="file-size">${formatBytes(file.size)}</span>
                    <span id="${pageCountId}" class="page-count-badge" style="display:none;">- P</span>
                </div>
            </div>
            <div class="card-actions">
                <div class="btn-mini" onclick="previewFile(${index})" title="Preview">👁️</div>
                <div class="btn-mini" onclick="replaceFile(${index})" title="Replace">🔄</div>
                <div class="btn-mini btn-danger" onclick="removeFile(${index})" title="Remove">✕</div>
            </div>
        `;
        
        // Drag Events
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragover', handleDragOver);
        card.addEventListener('drop', handleDrop);
        card.addEventListener('dragenter', handleDragEnter);
        card.addEventListener('dragleave', handleDragLeave);

        grid.appendChild(card);

        // Render PDF Thumbnail & Get Page Count
        // Slight delay to ensure DOM layout is ready for width calc
        setTimeout(() => renderThumbnail(file.url, canvasId, `loader-${index}`, pageCountId), 0);
    });
    
    container.appendChild(grid);
}

// ... (renderThumbnail, formatBytes, drag handlers) ...

async function handleFileUpload(e) {
    // ... existing ...
}

async function renderThumbnail(url, canvasId, loaderId, pageCountId) {
    try {
        const loadingTask = pdfjsLib.getDocument(url);
        const pdf = await loadingTask.promise;
        
        // Update Page Count
        if (pageCountId) {
            const badge = document.getElementById(pageCountId);
            if (badge) {
                badge.innerText = `${pdf.numPages} P`;
                badge.style.display = 'inline-block';
            }
        }

        const page = await pdf.getPage(1);
        const canvas = document.getElementById(canvasId);
        if(!canvas) return; 

        // Dynamic Scale Calculation
        const wrapper = canvas.parentElement;
        const targetWidth = wrapper.clientWidth || 150; 
        
        // Get viewport at scale 1 to measure natural size
        const unscaledViewport = page.getViewport({scale: 1});
        // Calculate scale to fit width (minus some padding if desired, or just fit)
        // We use slightly larger scale for crispness on retina
        const scale = (targetWidth / unscaledViewport.width) * 1.5;
        
        const viewport = page.getViewport({scale: scale});

        const context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        // Center the canvas if needed (handled by flex parent, but good to be explicit)
        
        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };
        await page.render(renderContext).promise;
        
        const loader = document.getElementById(loaderId);
        if(loader) loader.style.display = 'none';

    } catch (err) {
        console.error("Error rendering thumb:", err);
        const l = document.getElementById(loaderId);
        if(l) l.innerText = "Preview N/A";
    }
}


function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

// Drag & Drop Logic
let dragSrcEl = null;

function handleDragStart(e) {
    dragSrcEl = this;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
    this.classList.add('dragging');
}

function handleDragOver(e) {
    if (e.preventDefault) e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    this.classList.add('over');
}

function handleDragLeave(e) {
    this.classList.remove('over');
}

function handleDrop(e) {
    if (e.stopPropagation) e.stopPropagation();
    
    if (dragSrcEl !== this) {
        // Swap Data in UI
        const srcIndex = parseInt(dragSrcEl.dataset.index);
        const targetIndex = parseInt(this.dataset.index);
        
        // Swap in global config
        const files = window.EDITOR_CONFIG.files;
        const temp = files[srcIndex];
        files[srcIndex] = files[targetIndex];
        files[targetIndex] = temp;
        
        // Re-render
        renderCanvas(files, TOOLS[window.EDITOR_CONFIG.tool].canvasMode);
    }
    return false;
}

function removeFile(index) {
    if (!confirm('Remove this file?')) return;
    window.EDITOR_CONFIG.files.splice(index, 1);
    renderCanvas(window.EDITOR_CONFIG.files, TOOLS[window.EDITOR_CONFIG.tool].canvasMode);
}

function renderRightPanel(items) {
    const container = document.getElementById('toolSettings');
    container.innerHTML = '';

    if (!items || items.length === 0) {
        container.innerHTML = '<p class="text-gray">No settings available.</p>';
        return;
    }

    items.forEach(item => {
        const group = document.createElement('div');
        group.className = 'control-group';
        
        const label = document.createElement('label');
        label.className = 'control-label';
        label.innerText = item.label;
        group.appendChild(label);

        if (item.type === 'slider') {
            const slider = document.createElement('input');
            slider.type = 'range';
            slider.min = item.min;
            slider.max = item.max;
            slider.value = item.value;
            slider.className = 'control-slider';
            group.appendChild(slider);
            
            // Add labels if present
            if (item.labels) {
                const labelContainer = document.createElement('div');
                labelContainer.style.display = 'flex';
                labelContainer.style.justifyContent = 'space-between';
                labelContainer.style.fontSize = '0.8rem';
                labelContainer.style.color = 'var(--gray)';
                item.labels.forEach(l => {
                    const span = document.createElement('span');
                    span.innerText = l;
                    labelContainer.appendChild(span);
                });
                group.appendChild(labelContainer);
            }
        } else if (item.type === 'info') {
             const p = document.createElement('p');
             p.style.fontSize = '0.9rem';
             p.style.color = 'var(--gray)';
             p.innerText = item.text;
             group.appendChild(p);
        }

        container.appendChild(group);
    });
}

// Helper Validation
function validateFile(file) {
    const MAX_SIZE = 50 * 1024 * 1024; // 50MB
    const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png'];
    
    if (file.size > MAX_SIZE) {
        displayStatus(`Error: ${file.name} is too large (>50MB)`, "error");
        return false;
    }
    // Simple check (extensions also good fallback)
    if (!ALLOWED_TYPES.includes(file.type) && !file.name.toLowerCase().endsWith('.pdf')) {
        console.warn("Unknown type:", file.type);
    }
    return true;
}

function handleToolAction(actionId, isTool) {
    console.log("Tool action:", actionId, "isTool:", isTool);
    
    // Special handling for Image Tool (needs file input)
    if (actionId === 'imageTool') {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/png, image/jpeg, image/jpg';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (f) => {
                if (typeof addImage === 'function') {
                    addImage(f.target.result);
                }
            };
            reader.readAsDataURL(file);
        };
        input.click();
        return;
    }
    
    // Signature Tool
    if (actionId === 'signatureTool') {
        if (typeof openSignatureModal === 'function') {
            openSignatureModal();
        }
        return;
    }

    // If it's a Fabric.js tool (text, draw, highlight, select)
    if (isTool && typeof setActiveTool === 'function') {
        setActiveTool(actionId);
        return;
    }
    
    // Standard actions
    switch(actionId) {
        case 'addFile':
            const input = getGlobalInput(handleFileUpload);
            input.click();
            break;
        case 'rotateLeft':
            rotateCurrentPage(-90);
            break;
        case 'rotateRight':
            rotateCurrentPage(90);
            break;
        case 'deletePage':
            deleteCurrentPage();
            break;
        default:
            console.log("Unknown action:", actionId);
    }
}

// Rotate current page (for advanced mode)
function rotateCurrentPage(angle) {
    displayStatus(`Rotating page by ${angle}°...`, "normal");
    // This would need backend integration for actual rotation
    // For now, just visual feedback
}

function deleteCurrentPage() {
    if(confirm('Delete this page?')) {
        displayStatus("Page marked for deletion", "normal");
    }
}

// Singleton Input Helper
function getGlobalInput(handler) {
    let input = document.getElementById('globalFileInput');
    if (!input) {
         input = document.createElement('input');
         input.type = 'file';
         input.id = 'globalFileInput';
         input.multiple = true;
         input.style.display = 'none';
         input.addEventListener('change', handler);
         document.body.appendChild(input);
    }
    // Reset to allow selecting same file again
    input.value = ''; 
    return input;
}

// Replace Logic
function replaceFile(index) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf, .jpg, .png';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        if (!validateFile(file)) return;
        
        displayStatus(`Replacing file ${index+1}...`);
        
        // Upload single file to session
        const formData = new FormData();
        formData.append('files[]', file);
        formData.append('session_id', window.EDITOR_CONFIG.sessionId);
        
        try {
            const res = await fetch('/api/upload-session', {
                method: 'POST',
                headers: {'X-CSRFToken': window.EDITOR_CONFIG.csrfToken},
                body: formData
            });
            const data = await res.json();
            if (data.success && data.files.length > 0) {
                // Replace in local state
                window.EDITOR_CONFIG.files[index] = data.files[0];
                renderCanvas(window.EDITOR_CONFIG.files, TOOLS[window.EDITOR_CONFIG.tool].canvasMode);
                displayStatus("File replaced", "success");
            }
        } catch(err) {
            displayStatus("Replace failed", "error");
        }
    };
    input.click();
}



// Preview Logic
function previewFile(index) {
    const file = window.EDITOR_CONFIG.files[index];
    if (!file) return;
    
    const modal = document.getElementById('preview-modal');
    const frame = document.getElementById('preview-frame');
    
    if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        frame.src = file.url + "#toolbar=0"; // Minimal UI
    } else {
        // For images or others
        frame.src = file.url;
    }
    
    modal.style.display = 'flex';
}

function closePreview() {
    const modal = document.getElementById('preview-modal');
    modal.style.display = 'none';
    document.getElementById('preview-frame').src = ''; // Stop video/iframe
}

// Page Editing Logic
function rotatePage(pageNum, angle) {
    const card = document.querySelector(`.file-card[data-page-num="${pageNum}"]`);
    if (!card) return;

    // Track rotation in config
    let config = getPageConfig(pageNum);
    config.rotation = (config.rotation || 0) + angle;
    config.rotation = config.rotation % 360; // Keep it 0-360

    // Visual Update
    const wrapper = card.querySelector('.file-preview-wrapper');
    const canvas = wrapper.querySelector('canvas');
    canvas.style.transform = `rotate(${config.rotation}deg)`;
    // Maybe adjust wrapper if 90/270 deg? For now simple CSS rotate works visually.
    
    updatePageConfig(pageNum, config);
    displayStatus(`Page ${pageNum} rotated.`, "normal");
}

function deletePage(pageNum) {
    const card = document.querySelector(`.file-card[data-page-num="${pageNum}"]`);
    if (!card) return;

    if(!confirm(`Delete page ${pageNum}?`)) return;

    // Visual Remove
    card.style.opacity = '0.3';
    card.style.pointerEvents = 'none'; // Disable interactions
    
    // Mark deleted in config
    let config = getPageConfig(pageNum);
    config.deleted = true;
    updatePageConfig(pageNum, config);
    
    displayStatus(`Page ${pageNum} marked for deletion.`, "normal");
}

function getPageConfig(pageNum) {
    if (!window.EDITOR_CONFIG.currentPageConfig) window.EDITOR_CONFIG.currentPageConfig = [];
    let cfg = window.EDITOR_CONFIG.currentPageConfig.find(c => c.pageNum === pageNum);
    if (!cfg) {
        cfg = { pageNum: pageNum, rotation: 0, deleted: false };
        window.EDITOR_CONFIG.currentPageConfig.push(cfg);
    }
    return cfg;
}

function updatePageConfig(pageNum, newConfig) {
    const index = window.EDITOR_CONFIG.currentPageConfig.findIndex(c => c.pageNum === pageNum);
    if (index !== -1) {
        window.EDITOR_CONFIG.currentPageConfig[index] = newConfig;
    }
}

// Zoom Logic
function updateZoom(delta) {
    if (!window.EDITOR_CONFIG.zoom) window.EDITOR_CONFIG.zoom = 1.0;
    
    let newZoom = window.EDITOR_CONFIG.zoom + delta;
    // Clamp between 0.5 (50%) and 2.0 (200%)
    newZoom = Math.min(Math.max(newZoom, 0.5), 2.0);
    
    window.EDITOR_CONFIG.zoom = newZoom;
    
    // Update Display
    const display = document.getElementById('zoomLevelDisplay');
    if (display) display.innerText = `${Math.round(newZoom * 100)}%`;
    
    // Apply Zoom (Standard 'zoom' works best for scrollbars on Chrome/Edge)
    const content = document.getElementById('canvasContent');
    if (content) {
        // Fallback for Firefox could be transform, but for now assuming Webkit/Blink
        content.style.zoom = newZoom;
        // content.style.transform = `scale(${newZoom})`; // Old way
    }
}

function setupGlobalEvents() {
    document.getElementById('processBtn').addEventListener('click', processFile);
    
    // Zoom Events
    const zoomIn = document.getElementById('zoomInBtn');
    const zoomOut = document.getElementById('zoomOutBtn');
    
    if(zoomIn) zoomIn.addEventListener('click', () => updateZoom(0.1));
    if(zoomOut) zoomOut.addEventListener('click', () => updateZoom(-0.1));
}

function displayStatus(msg, type='normal') {
    const el = document.getElementById('statusText');
    if(el) {
        el.innerText = msg;
        if (type === 'error') el.style.color = 'var(--danger)';
        else el.style.color = 'var(--dark)';
    }
}

async function handleFileUpload(e) {
    const files = e.target.files;
    if (files.length === 0) return;

    displayStatus("Uploading files...", "normal");
    
    // Check if we have a session ID
    // If usage is 'new', we MUST redirect.
    // If usage is existing session, we CAN just update state.
    const isNew = window.EDITOR_CONFIG.sessionId === 'new';

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files[]', files[i]);
    }
    
    // If existing session, append ID to URL or similar?
    // Our View: api_upload_session creates NEW session every time?
    // No, we need to upload to CURRENT session if possible. 
    // BUT api_upload_session generates a new UUID.
    // We need to modify `api_upload_session` to accept an existing ID?
    // Or just let it create a new one if 'new'.
    
    // UPDATE: We need to support uploading to invalid/current session?
    // The current api_upload_session *always* makes a new session.
    // Let's modify it to accept optional session_id.
    
    // For now, let's look at the View. 
    // It creates `session_id = str(uuid.uuid4())`.
    
    // FIX: Client side logic depends on Backend. 
    // I will assume for now we use the "Append Logic" by sending session_id if available.
    
    let url = '/api/upload-session';
    if (!isNew) {
        formData.append('session_id', window.EDITOR_CONFIG.sessionId);
    }
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': window.EDITOR_CONFIG.csrfToken
            }
        });
        
        const data = await response.json();
        if (data.success) {
            if (isNew) {
                // Redirect to the new session URL
                const tool = window.EDITOR_CONFIG.tool;
                window.location.href = `/editor/${tool}/${data.session_id}`;
            } else {
                 // Append files locally
                 if (data.files) {
                     window.EDITOR_CONFIG.files.push(...data.files);
                     renderCanvas(window.EDITOR_CONFIG.files, TOOLS[window.EDITOR_CONFIG.tool].canvasMode);
                     displayStatus("Files added", "success");
                 }
            }
        } else {
            displayStatus("Upload failed: " + data.error, "error");
        }
    } catch (err) {
        console.error(err);
        displayStatus("Upload error", "error");
    }
}

async function processFile() {
    const btn = document.getElementById('processBtn');
    const originalText = btn.innerText;
    btn.innerText = 'Processing...';
    btn.disabled = true;

    const config = window.EDITOR_CONFIG;
    const toolConfig = TOOLS[config.tool];
    
    try {
        let endpoint, payload;
        
        // Check if we're in advanced editing mode with layers
        if (toolConfig && toolConfig.canvasMode === 'advanced' && typeof exportLayersJSON === 'function') {
            // Export Fabric.js layers and call editor apply API
            const layers = exportLayersJSON();
            endpoint = `/api/editor/apply/${config.sessionId}`;
            payload = { layers: layers };
            displayStatus(`Exporting ${layers.length} annotation(s)...`, "normal");
        } else {
            // Standard processing
            endpoint = `/api/process-session/${config.tool}/${config.sessionId}`;
            payload = {
                files: config.files.map(f => f.name),
                pages_config: config.currentPageConfig || []
            };
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            displayStatus("Error: " + data.error, "error");
            btn.innerText = originalText;
            btn.disabled = false;
        }
    } catch (err) {
        console.error(err);
        displayStatus("Network connection error", "error");
        btn.innerText = originalText;
        btn.disabled = false;
    }
}
