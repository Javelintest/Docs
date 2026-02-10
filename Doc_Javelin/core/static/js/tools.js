/**
 * Tool Configuration Registry
 * Defines available tools, their icons, and settings panels.
 */
const TOOLS = {
    'compress': {
        name: 'Compress PDF',
        leftPanel: [], // No specific left tools
        rightPanel: [
            {
                type: 'slider',
                id: 'compressionLevel',
                label: 'Compression Level',
                min: 0,
                max: 2, // 0: Low, 1: Medium, 2: High
                value: 1, 
                labels: ['Low', 'Medium', 'High']
            }
        ],
        processEndpoint: '/api/compress'
    },
    'edit_pdf': {
        name: 'Edit PDF',
        canvasMode: 'advanced', // New advanced mode with Fabric.js overlay
        leftPanel: [
            { id: 'selectTool', icon: '<i class="ri-cursor-line"></i>', title: 'Select', tool: true },
            { id: 'textEditTool', icon: '<i class="ri-text-spacing"></i>', title: 'Edit Text (Beta)', tool: true },
            { id: 'textTool', icon: '<i class="ri-text"></i>', title: 'Add Text', tool: true },
            { id: 'imageTool', icon: '<i class="ri-image-add-line"></i>', title: 'Add Image', tool: true },
            { id: 'signatureTool', icon: '<i class="ri-pen-nib-line"></i>', title: 'Add Signature', tool: true },
            { id: 'drawTool', icon: '<i class="ri-pencil-line"></i>', title: 'Draw', tool: true },
            { id: 'highlightTool', icon: '<i class="ri-mark-pen-line"></i>', title: 'Highlight', tool: true },
            { id: 'separator', type: 'separator' },
            { id: 'rotateLeft', icon: '<i class="ri-anticlockwise-2-line"></i>', title: 'Rotate Left' },
            { id: 'rotateRight', icon: '<i class="ri-clockwise-2-line"></i>', title: 'Rotate Right' },
            { id: 'deletePage', icon: '<i class="ri-delete-bin-line"></i>', title: 'Delete Page' }
        ],
        rightPanel: [
            {
                type: 'info',
                label: 'Properties',
                text: 'Select an object to edit properties.'
            }
        ],
        processEndpoint: '/api/edit-pdf'
    },
    'merge': {
        name: 'Merge PDF',
        canvasMode: 'grid',
        leftPanel: [
            { id: 'addFile', icon: '📂', title: 'Add Another File' }
        ],
        rightPanel: [
             {
                type: 'info',
                label: 'Order',
                text: 'Drag and drop files to reorder.'
            }
        ],
        processEndpoint: '/api/merge'
    },
    'pdf2word': {
        name: 'PDF to Word',
        leftPanel: [],
        rightPanel: [
             {
                type: 'info',
                label: 'Conversion',
                text: 'Convert PDF documents to editable Microsoft Word files.'
            }
        ],
        processEndpoint: '/api/pdf2word'
    },
    'pdf2excel': {
        name: 'PDF to Excel',
        leftPanel: [],
        rightPanel: [
             {
                type: 'info',
                label: 'Conversion',
                text: 'Extract tables from PDF to Microsoft Excel spreadsheets.'
            }
        ],
        processEndpoint: '/api/pdf2excel'
    },
    'img2pdf': {
        name: 'Image to PDF',
        canvasMode: 'grid',
        leftPanel: [
             { id: 'addFile', icon: '➕', title: 'Add Image' }
        ],
        rightPanel: [
             {
                type: 'info',
                label: 'Info',
                text: 'Drag to reorder images.'
            }
        ],
        processEndpoint: '/api/img2pdf'
    }
    // Add other tools here...
};
