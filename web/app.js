// State variables
let selectedFile = null;
let extractedJsonData = null;

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const selectedFileName = document.getElementById('selected-file-name');
const fileDetails = document.getElementById('file-details');
const btnClearFile = document.getElementById('btn-clear-file');
const btnExtract = document.getElementById('btn-extract');

const stateIdle = document.getElementById('state-idle');
const stateLoading = document.getElementById('state-loading');
const stateError = document.getElementById('state-error');
const stateResults = document.getElementById('state-results');

const loadingStatus = document.getElementById('loading-status');
const stepRender = document.getElementById('step-render');
const stepVlm = document.getElementById('step-vlm');
const stepSchema = document.getElementById('step-schema');

const errorMessage = document.getElementById('error-message');
const btnRetry = document.getElementById('btn-retry');

const tagFilename = document.getElementById('tag-filename');
const tagPartnumber = document.getElementById('tag-partnumber');
const tagPin = document.getElementById('tag-pin');
const btnDownloadJson = document.getElementById('btn-download-json');

// Table Value Cells
const valueIds = [
    'part_number', 'min_operating_temp_c', 'max_operating_temp_c',
    'max_length_mm', 'max_width_mm', 'max_height_mm', 'pin_number',
    'io_if_a', 'vf_v', 'vrrm_v', 'ir_a'
];

// Helper to switch view states
function switchState(stateName) {
    [stateIdle, stateLoading, stateError, stateResults].forEach(el => el.classList.remove('active'));
    
    if (stateName === 'idle') stateIdle.classList.add('active');
    if (stateName === 'loading') stateLoading.classList.add('active');
    if (stateName === 'error') stateError.classList.add('active');
    if (stateName === 'results') stateResults.classList.add('active');
}

// Drag & Drop Event Listeners
['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    }, false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

dropZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    if (fileInput.files.length > 0) {
        handleFileSelect(fileInput.files[0]);
    }
});

// Handle File Selection
function handleFileSelect(file) {
    if (file.type !== 'application/pdf' && !file.name.lowerCase().endsWith('.pdf')) {
        alert('請選擇 PDF 檔案！');
        return;
    }
    selectedFile = file;
    selectedFileName.textContent = file.name;
    fileDetails.style.display = 'flex';
    btnExtract.disabled = false;
    
    // Smooth transition
    dropZone.style.borderColor = 'rgba(16, 185, 129, 0.4)';
    dropZone.style.background = 'rgba(16, 185, 129, 0.03)';
}

// Clear selected file
function clearSelectedFile() {
    selectedFile = null;
    fileInput.value = '';
    fileDetails.style.display = 'none';
    btnExtract.disabled = true;
    
    // Restore drop zone styling
    dropZone.style.borderColor = '';
    dropZone.style.background = '';
    
    switchState('idle');
}

btnClearFile.addEventListener('click', (e) => {
    e.stopPropagation();
    clearSelectedFile();
});

// Retry upload
btnRetry.addEventListener('click', () => {
    switchState('idle');
});

// Simulate pipeline steps
function updateProgress(step, text) {
    loadingStatus.textContent = text;
    
    [stepRender, stepVlm, stepSchema].forEach(el => {
        el.classList.remove('active', 'completed');
    });
    
    if (step === 1) {
        stepRender.classList.add('active');
    } else if (step === 2) {
        stepRender.classList.add('completed');
        stepVlm.classList.add('active');
    } else if (step === 3) {
        stepRender.classList.add('completed');
        stepVlm.classList.add('completed');
        stepSchema.classList.add('active');
    }
}

// Upload & Call Extraction API
btnExtract.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    switchState('loading');
    updateProgress(1, '正在將 PDF 轉譯為高解析度圖面...');
    
    // Simulate step timing (FastAPI handles it asynchronously, we just coordinate UI logs)
    const vlmTimer = setTimeout(() => {
        updateProgress(2, '正在利用 Gemini 2.5 Flash VLM 辨識物理與電性特徵...');
    }, 2500);
    
    const schemaTimer = setTimeout(() => {
        updateProgress(3, '正在套用 JSON Schema 強制校對結構化欄位...');
    }, 6000);
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        // Clear simulated timers
        clearTimeout(vlmTimer);
        clearTimeout(schemaTimer);
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'API 伺服器回傳錯誤');
        }
        
        const data = await response.json();
        extractedJsonData = data;
        
        // Populate Result UI
        tagFilename.textContent = `檔名: ${data.filename}`;
        tagPartnumber.textContent = `型號: ${data.part_number || '無法判斷'}`;
        tagPin.textContent = `引腳數: ${data.pin_number ? data.pin_number + ' Pins' : '未知'}`;
        
        valueIds.forEach(id => {
            const cell = document.getElementById(`val-${id}`);
            if (cell) {
                const val = data[id];
                cell.textContent = (val !== null && val !== undefined && val !== '') ? val : '無 (N/A)';
            }
        });
        
        switchState('results');
        
    } catch (err) {
        clearTimeout(vlmTimer);
        clearTimeout(schemaTimer);
        errorMessage.textContent = err.message;
        switchState('error');
    }
});

// Download JSON Handler
btnDownloadJson.addEventListener('click', () => {
    if (!extractedJsonData) return;
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(extractedJsonData, null, 4));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    
    // Use part number for filename if available
    const outputName = extractedJsonData.part_number 
        ? `${extractedJsonData.part_number}_extracted.json` 
        : "datasheet_extracted.json";
        
    downloadAnchor.setAttribute("download", outputName);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
});
