/**
 * Inspector Mode Logic
 * Handles PDF text analysis and "True Editing" (Redact & Replace)
 */

let inspectorOverlays = [];
let isInspectorActive = false;
let cachedPageAnalysis = {}; // Cache analysis per page

async function enableInspectorMode() {
    if (isInspectorActive) return;
    isInspectorActive = true;
    console.log("Inspector Mode Active");

    const pageNum = window.EDITOR_STATE.currentPage;
    const sessionId = window.EDITOR_CONFIG.sessionId;

    displayStatus("Analyzing text...", "normal");

    // Check cache
    if (!cachedPageAnalysis[pageNum]) {
        try {
            const response = await fetch(`/api/analyze-pdf/${sessionId}/${pageNum}`);
            const data = await response.json();
            
            if (data.success) {
                cachedPageAnalysis[pageNum] = data.text_blocks;
            } else {
                displayStatus("Text analysis failed", "error");
                return;
            }
        } catch (e) {
            console.error("Analysis error:", e);
            displayStatus("Error analyzing text", "error");
            return;
        }
    }

    renderInspectorOverlays(cachedPageAnalysis[pageNum]);
    displayStatus("Click text to edit", "success");
}

function disableInspectorMode() {
    isInspectorActive = false;
    clearInspectorOverlays();
}

function renderInspectorOverlays(blocks) {
    const fc = window.EDITOR_STATE.fabricCanvas;
    if (!fc || !blocks) return;

    // PDF.js vs Fabric.js coordinate system match
    // PyMuPDF coordinates are usually 72 DPI (Points)
    // We need to ensure they match the canvas dimensions
    // The canvas is resized to match the PDF viewer container
    // We might need a scaling factor if the PDF.js rendering scale != 1
    
    // Simple heuristic: Get canvas width vs PDF Page width (if known)
    // Ideally, PyMuPDF coords (pts) * scale = Canvas coords (px)
    // We can infer scale from one block or just assume standard 72DPI to 96DPI conversion or similar
    // Actually, fabric-overlay.js fits canvas to container.
    // We'll assume for now 1:1 match or close enough, and refine if offset.

    blocks.forEach(block => {
        const [x0, y0, x1, y1] = block.bbox;
        const width = x1 - x0;
        const height = y1 - y0;

        // Interactive Overlay Rect
        const rect = new fabric.Rect({
            left: x0,
            top: y0,
            width: width,
            height: height,
            fill: 'transparent',
            stroke: 'transparent',
            strokeWidth: 1,
            selectable: false,
            hoverCursor: 'text',
            data: block, // Store original text data
            isInspectorInfo: true
        });

        rect.on('mouseover', () => {
             rect.set('stroke', '#3b82f6'); // Blue highlight
             rect.set('fill', 'rgba(59, 130, 246, 0.1)');
             fc.renderAll();
        });

        rect.on('mouseout', () => {
             rect.set('stroke', 'transparent');
             rect.set('fill', 'transparent');
             fc.renderAll();
        });

        rect.on('mousedown', () => {
            convertTextToEditable(rect);
        });

        fc.add(rect);
        inspectorOverlays.push(rect);
    });

    fc.renderAll();
}

function clearInspectorOverlays() {
    const fc = window.EDITOR_STATE.fabricCanvas;
    if (!fc) return;

    inspectorOverlays.forEach(obj => fc.remove(obj));
    inspectorOverlays = [];
    fc.renderAll();
}

function convertTextToEditable(overlayRect) {
    const fc = window.EDITOR_STATE.fabricCanvas;
    const data = overlayRect.data; // {text, bbox, font, size, color}
    
    // 1. Remove the overlay
    fc.remove(overlayRect);
    
    // 2. Add Whiteout Rect (to hide original) calls existing 'addLayer' logic implicitly if we create object?
    // We need a specific "Redact" layer type if we want to be explicit, 
    // OR just a white rectangle shape.
    
    const whiteout = new fabric.Rect({
        left: overlayRect.left,
        top: overlayRect.top,
        width: overlayRect.width,
        height: overlayRect.height + 2, // slightly larger to cover artifacts
        fill: '#ffffff',
        selectable: false,
        evented: false
    });
    fc.add(whiteout);
    
    // Add whiteout to layers
    addLayer({
        type: 'rect', // treated as shape
        object: whiteout,
        pageNum: window.EDITOR_STATE.currentPage,
        fill: '#ffffff'
    });

    // 3. Add Editable Text on top
    const editableText = new fabric.IText(data.text, {
        left: overlayRect.left,
        top: overlayRect.top, // adjustment for baseline might be needed
        fontFamily: 'Inter', // Fallback, mapping PDF fonts is hard
        fontSize: data.size, // PyMuPDF size is usually accurate
        fill: data.color,
        editable: true
    });
    
    fc.add(editableText);
    fc.setActiveObject(editableText);
    editableText.enterEditing();
    editableText.selectAll();
    
    // Add text to layers
    addLayer({
        type: 'text',
        object: editableText,
        pageNum: window.EDITOR_STATE.currentPage
    });
    
    fc.renderAll();
    
    // Switch tool to select to allow editing
    if (typeof setActiveTool === 'function') {
        setActiveTool('selectTool');
    }
}
