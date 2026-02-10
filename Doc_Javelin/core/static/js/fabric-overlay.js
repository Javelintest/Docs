/**
 * Fabric.js Overlay Manager
 * Manages Fabric canvas overlays for PDF editing.
 */

// Global state for editor layers
window.EDITOR_STATE = window.EDITOR_STATE || {
    layers: [],
    activeTool: null,
    fabricCanvas: null,
    currentPage: 1
};

/**
 * Initialize Fabric.js canvas overlay on top of PDF viewer
 */
function initFabricOverlay(containerSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) {
        console.error("Fabric overlay container not found:", containerSelector);
        return null;
    }
    
    // Create canvas element
    const canvasEl = document.createElement('canvas');
    canvasEl.id = 'fabric-canvas';
    canvasEl.style.position = 'absolute';
    canvasEl.style.top = '0';
    canvasEl.style.left = '0';
    canvasEl.style.pointerEvents = 'none'; // Start disabled, enable when tool active
    canvasEl.style.zIndex = '100';
    
    container.style.position = 'relative';
    container.appendChild(canvasEl);
    
    // Match canvas size to container
    const rect = container.getBoundingClientRect();
    canvasEl.width = rect.width;
    canvasEl.height = rect.height;
    
    // Initialize Fabric.js
    const fabricCanvas = new fabric.Canvas('fabric-canvas', {
        selection: true,
        preserveObjectStacking: true
    });
    
    window.EDITOR_STATE.fabricCanvas = fabricCanvas;
    
    // Resize handler
    window.addEventListener('resize', () => {
        const newRect = container.getBoundingClientRect();
        fabricCanvas.setWidth(newRect.width);
        fabricCanvas.setHeight(newRect.height);
        fabricCanvas.renderAll();
    });
    
    console.log("Fabric overlay initialized");
    return fabricCanvas;
}

/**
 * Enable/Disable canvas interaction
 */
function setCanvasInteractive(enabled) {
    const canvas = document.getElementById('fabric-canvas');
    if (canvas) {
        canvas.style.pointerEvents = enabled ? 'auto' : 'none';
    }
}

/**
 * Set active tool
 */
function setActiveTool(toolId) {
    window.EDITOR_STATE.activeTool = toolId;
    const fc = window.EDITOR_STATE.fabricCanvas;
    
    if (!fc) return;
    
    // Reset modes
    fc.isDrawingMode = false;
    fc.selection = true;
    setCanvasInteractive(true);
    
    // Disable Inspector Mode by default when switching tools
    if (typeof disableInspectorMode === 'function' && toolId !== 'textEditTool') {
        disableInspectorMode();
    }

    switch(toolId) {
        case 'textEditTool':
            fc.defaultCursor = 'default';
            if (typeof enableInspectorMode === 'function') {
                enableInspectorMode();
            }
            break;
        case 'textTool':
            fc.defaultCursor = 'text';
            displayStatus("Click to add text box", "normal");
            break;
        case 'drawTool':
            fc.isDrawingMode = true;
            fc.freeDrawingBrush.color = '#000000';
            fc.freeDrawingBrush.width = 2;
            displayStatus("Draw on the canvas", "normal");
            break;
        case 'highlightTool':
            fc.isDrawingMode = true;
            fc.freeDrawingBrush.color = 'rgba(255, 255, 0, 0.4)';
            fc.freeDrawingBrush.width = 20;
            displayStatus("Highlight text", "normal");
            break;
        case 'selectTool':
            fc.defaultCursor = 'default';
            displayStatus("Select and edit objects", "normal");
            break;
        default:
            setCanvasInteractive(false);
            break;
    }
    
    // Update toolbar active state
    document.querySelectorAll('.tool-icon').forEach(el => el.classList.remove('active'));
    const activeBtn = document.querySelector(`[data-tool="${toolId}"]`);
    if (activeBtn) activeBtn.classList.add('active');
}

/**
 * Add text box at click position
 */
function addTextBox(x, y, text = 'Edit me') {
    const fc = window.EDITOR_STATE.fabricCanvas;
    if (!fc) return;
    
    const textBox = new fabric.IText(text, {
        left: x,
        top: y,
        fontFamily: 'Inter',
        fontSize: 16,
        fill: '#000000',
        editable: true,
        padding: 5,
        backgroundColor: 'rgba(255,255,255,0.8)'
    });
    
    fc.add(textBox);
    fc.setActiveObject(textBox);
    textBox.enterEditing();
    textBox.selectAll();
    fc.renderAll();
    
    // Add to layers
    addLayer({
        type: 'text',
        object: textBox,
        pageNum: window.EDITOR_STATE.currentPage
    });
    
    return textBox;
}

/**
 * Add image to canvas
 */
function addImage(url) {
    const fc = window.EDITOR_STATE.fabricCanvas;
    if (!fc) return;
    
    fabric.Image.fromURL(url, function(img) {
        // Resize if too big
        if (img.width > 300) {
            img.scaleToWidth(300);
        }
        
        img.set({
            left: 100,
            top: 100
        });
        
        fc.add(img);
        fc.setActiveObject(img);
        fc.renderAll();
        
        // Add to layers
        addLayer({
            type: 'image',
            object: img,
            pageNum: window.EDITOR_STATE.currentPage
        });
    });
}

/**
 * Add layer to state
 */
function addLayer(layerData) {
    layerData.id = 'layer-' + Date.now();
    window.EDITOR_STATE.layers.push(layerData);
    console.log("Layer added:", layerData.id);
}

/**
 * Get all layers as JSON for export
 */
function exportLayersJSON() {
    const fc = window.EDITOR_STATE.fabricCanvas;
    if (!fc) return [];
    
    const layers = [];
    fc.getObjects().forEach((obj, idx) => {
        const layer = {
            id: 'layer-' + idx,
            pageNum: window.EDITOR_STATE.currentPage,
            type: obj.type === 'i-text' ? 'text' : obj.type,
            left: obj.left,
            top: obj.top,
            scaleX: obj.scaleX,
            scaleY: obj.scaleY,
            angle: obj.angle
        };
        
        if (obj.type === 'i-text') {
            layer.text = obj.text;
            layer.fontSize = obj.fontSize;
            layer.fontFamily = obj.fontFamily;
            layer.fill = obj.fill;
        } else if (obj.type === 'path') {
            layer.path = obj.path;
            layer.stroke = obj.stroke;
            layer.strokeWidth = obj.strokeWidth;
        } else if (obj.type === 'image') {
           // For images, we need the original source
           // This assumes we have the src or dataURL available
           layer.src = obj.getSrc();
           // PyMuPDF needs to know if it's base64 or URL
           layer.width = obj.width * obj.scaleX;
           layer.height = obj.height * obj.scaleY;
        } else if (obj.type === 'rect') {
            layer.width = obj.width;
            layer.height = obj.height;
            layer.fill = obj.fill;
            layer.stroke = obj.stroke;
            layer.strokeWidth = obj.strokeWidth;
        }
        
        layers.push(layer);
    });
    
    return layers;
}

/**
 * Clear all objects from canvas
 */
function clearCanvas() {
    const fc = window.EDITOR_STATE.fabricCanvas;
    if (fc) {
        fc.clear();
        window.EDITOR_STATE.layers = [];
    }
}

// Canvas click handler for adding text
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const fc = window.EDITOR_STATE.fabricCanvas;
        if (fc) {
            fc.on('mouse:down', function(options) {
                if (window.EDITOR_STATE.activeTool === 'textTool' && !options.target) {
                    const pointer = fc.getPointer(options.e);
                    addTextBox(pointer.x, pointer.y);
                    setActiveTool('selectTool'); // Switch to select after adding
                }
            });
            
            // Object selection - update right panel
            fc.on('selection:created', updatePropertiesPanel);
            fc.on('selection:updated', updatePropertiesPanel);
            fc.on('selection:cleared', clearPropertiesPanel);
        }
    }, 1000); // Delay to ensure canvas is initialized
});

/**
 * Update properties panel based on selected object
 */
function updatePropertiesPanel() {
    const fc = window.EDITOR_STATE.fabricCanvas;
    if (!fc) return;
    
    const activeObj = fc.getActiveObject();
    if (!activeObj) return;
    
    const panel = document.getElementById('toolSettings');
    if (!panel) return;
    
    let html = '<div class="control-group"><label class="control-label">Object Properties</label>';
    
    if (activeObj.type === 'i-text') {
        html += `
            <div style="margin-bottom: 12px;">
                <label style="font-size: 0.8rem; color: var(--gray); display: block; margin-bottom: 4px;">Font Size</label>
                <input type="number" id="prop-fontSize" value="${activeObj.fontSize}" 
                       style="width: 100%; padding: 6px; border: 1px solid var(--border); border-radius: 4px;"
                       onchange="updateObjectProperty('fontSize', parseInt(this.value))">
            </div>
            <div style="margin-bottom: 12px;">
                <label style="font-size: 0.8rem; color: var(--gray); display: block; margin-bottom: 4px;">Color</label>
                <input type="color" id="prop-color" value="${activeObj.fill}" 
                       style="width: 100%; height: 36px; border: 1px solid var(--border); border-radius: 4px;"
                       onchange="updateObjectProperty('fill', this.value)">
            </div>
        `;
    }
    
    html += `
        <div style="margin-bottom: 12px;">
            <label style="font-size: 0.8rem; color: var(--gray); display: block; margin-bottom: 4px;">Opacity</label>
            <input type="range" id="prop-opacity" min="0" max="1" step="0.1" value="${activeObj.opacity || 1}" 
                   style="width: 100%;"
                   onchange="updateObjectProperty('opacity', parseFloat(this.value))">
        </div>
        <button class="btn-secondary" style="width: 100%; margin-top: 8px;" onclick="deleteSelectedObject()">🗑️ Delete</button>
    `;
    
    html += '</div>';
    panel.innerHTML = html;
}

/**
 * Update property of selected object
 */
function updateObjectProperty(prop, value) {
    const fc = window.EDITOR_STATE.fabricCanvas;
    if (!fc) return;
    
    const activeObj = fc.getActiveObject();
    if (activeObj) {
        activeObj.set(prop, value);
        fc.renderAll();
    }
}

/**
 * Delete selected object
 */
function deleteSelectedObject() {
    const fc = window.EDITOR_STATE.fabricCanvas;
    if (!fc) return;
    
    const activeObj = fc.getActiveObject();
    if (activeObj) {
        fc.remove(activeObj);
        fc.renderAll();
        clearPropertiesPanel();
    }
}

/**
 * Clear properties panel
 */
function clearPropertiesPanel() {
    const panel = document.getElementById('toolSettings');
    if (panel) {
        panel.innerHTML = '<p class="text-gray" style="font-size: 0.9rem; color: var(--gray);">Select an object to edit properties.</p>';
    }
}
