/**
 * Signature Tool Logic
 * Handles the signature modal, drawing pad, and adding signatures to the main canvas.
 */

let sigPadCanvas = null;
let currentSigTab = 'draw';
let currentFont = 'Great Vibes';

// Initialize when modal opens
function initSignaturePad() {
    if (sigPadCanvas) {
        sigPadCanvas.clear();
        return;
    }

    const container = document.getElementById('sig-pad-container');
    const canvasEl = document.createElement('canvas');
    canvasEl.id = 'sig-canvas';
    // Match container size
    const rect = container.getBoundingClientRect();
    canvasEl.width = rect.width;
    canvasEl.height = rect.height;
    
    container.appendChild(canvasEl);

    sigPadCanvas = new fabric.Canvas('sig-canvas', {
        isDrawingMode: true,
        backgroundColor: 'transparent'
    });
    
    sigPadCanvas.freeDrawingBrush.width = 3;
    sigPadCanvas.freeDrawingBrush.color = '#000000';
}

function openSignatureModal() {
    document.getElementById('signature-modal').style.display = 'flex';
    // Init canvas after modal is visible so dimensions are correct
    setTimeout(() => {
        initSignaturePad();
        switchSigTab('draw'); // Reset to draw tab
    }, 100);
}

function closeSignatureModal() {
    document.getElementById('signature-modal').style.display = 'none';
}

function switchSigTab(tab) {
    currentSigTab = tab;
    
    // UI Updates
    document.querySelectorAll('.modal-tab').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    
    // Find index logic or simple selector
    const tabs = ['draw', 'type', 'upload'];
    document.querySelectorAll('.modal-tab')[tabs.indexOf(tab)].classList.add('active');
    document.getElementById(`sig-${tab}`).classList.add('active');
}

function clearSignaturePad() {
    if (sigPadCanvas) sigPadCanvas.clear();
}

function updateSigPreview(text) {
    const preview = document.getElementById('sig-type-preview');
    preview.innerText = text || 'Signature';
    preview.style.fontFamily = currentFont;
}

function changeSigFont(fontName) {
    currentFont = fontName;
    const preview = document.getElementById('sig-type-preview');
    preview.style.fontFamily = fontName;
}

// Upload Handling
document.getElementById('sig-upload-input').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(f) {
        const img = document.createElement('img');
        img.src = f.target.result;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '150px';
        
        const preview = document.getElementById('sig-upload-preview');
        preview.innerHTML = '';
        preview.appendChild(img);
        // Store for "Add" click
        preview.dataset.url = f.target.result;
    };
    reader.readAsDataURL(file);
});

async function addSignatureToCanvas() {
    let dataUrl = null;

    if (currentSigTab === 'draw') {
        if (!sigPadCanvas || sigPadCanvas.getObjects().length === 0) {
            alert("Please draw a signature first.");
            return;
        }
        // Export just the drawing
        dataUrl = sigPadCanvas.toDataURL({
            format: 'png',
            multiplier: 2 // Better quality
        });
        
    } else if (currentSigTab === 'type') {
        const text = document.getElementById('sig-nav-input').value;
        if (!text) {
            alert("Please type your name.");
            return;
        }
        // convert text to image using a temp canvas
        dataUrl = textToImage(text, currentFont);
        
    } else if (currentSigTab === 'upload') {
        const preview = document.getElementById('sig-upload-preview');
        dataUrl = preview.dataset.url;
        if (!dataUrl) {
            alert("Please upload an image.");
            return;
        }
    }

    if (dataUrl && typeof addImage === 'function') {
        addImage(dataUrl);
        closeSignatureModal();
    }
}

function textToImage(text, font) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Calc size
    ctx.font = `60px "${font}"`;
    const width = ctx.measureText(text).width + 20;
    const height = 100; // Approx
    
    canvas.width = width;
    canvas.height = height;
    
    // Draw
    ctx.font = `60px "${font}"`;
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'black';
    ctx.fillText(text, 10, height/2);
    
    return canvas.toDataURL('image/png');
}
