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
        leftPanel: [
            { id: 'addPage', icon: '➕', title: 'Add Page' },
            { id: 'deletePage', icon: '🗑️', title: 'Delete Page' },
            { id: 'rotateLeft', icon: '↺', title: 'Rotate Left' },
            { id: 'rotateRight', icon: '↻', title: 'Rotate Right' }
        ],
        rightPanel: [
            {
                type: 'info',
                label: 'Info',
                text: 'Select pages to rotate or delete.'
            }
        ],
        canvasMode: 'pages', // New mode for Page Grid
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
