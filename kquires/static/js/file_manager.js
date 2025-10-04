// file_manager.js

// Utility functions
function showAlert(type, message) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the card body
    const cardBody = document.querySelector('.card-body');
    if (cardBody) {
        cardBody.insertBefore(alertDiv, cardBody.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Global function definitions
function handleUploadClick() {
    console.log('handleUploadClick function called!');
    const fileInput = document.getElementById('pdfFileInput');
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please select PDF files first!\n\n1. Click "Choose Files" above\n2. Select PDF files from your computer\n3. Then click "Save & Upload to Google Drive"');
        return;
    }
    
    // Show upload status
    const uploadStatus = document.getElementById('uploadStatus');
    const statusText = document.getElementById('statusText');
    const progressBar = document.getElementById('progressBar');
    
    if (uploadStatus) uploadStatus.style.display = 'block';
    if (statusText) statusText.textContent = `Uploading ${fileInput.files.length} file(s)...`;
    if (progressBar) progressBar.style.width = '0%';
    
    // Upload each file
    const files = Array.from(fileInput.files);
    let completedFiles = 0;
    
    files.forEach((file, index) => {
        uploadSingleFile(file, index + 1, files.length);
    });
    
    function uploadSingleFile(file, currentIndex, totalFiles) {
        const formData = new FormData();
        formData.append('pdf_file', file);
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken.value);
        }
        
        fetch('/articles/upload-pdf/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken ? csrfToken.value : ''
            }
        })
        .then(response => response.json())
        .then(data => {
            completedFiles++;
            const progress = Math.round((completedFiles / totalFiles) * 100);
            if (progressBar) progressBar.style.width = progress + '%';
            
            if (data.success) {
                if (statusText) {
                    statusText.innerHTML = `✅ File ${currentIndex}/${totalFiles}: ${file.name}<br>✓ Uploaded successfully`;
                }
                alert(`✅ File ${currentIndex}/${totalFiles}: "${file.name}" uploaded successfully!`);
            } else {
                if (statusText) {
                    statusText.innerHTML = `❌ File ${currentIndex}/${totalFiles}: ${file.name}<br>Error: ${data.message}`;
                }
                alert(`❌ File ${currentIndex}/${totalFiles}: "${file.name}" failed - ${data.message}`);
            }
            
            // If all files completed
            if (completedFiles === totalFiles) {
                setTimeout(() => {
                    alert(`Upload completed!\n\n${completedFiles}/${totalFiles} files processed successfully.`);
                    window.location.reload();
                }, 2000);
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            completedFiles++;
            if (statusText) {
                statusText.innerHTML = `❌ Error uploading ${file.name}: ${error.message}`;
            }
            alert(`❌ Error uploading "${file.name}": ${error.message}`);
            
            if (completedFiles === totalFiles) {
                alert('Upload completed with some errors. Check the status above.');
            }
        });
    }
}

// Test functions
function testUpload() {
    const fileInput = document.getElementById('pdfFileInput');
    if (fileInput.files && fileInput.files.length > 0) {
        alert(`Test: Found ${fileInput.files.length} files selected.`);
    } else {
        alert('Test: No files selected. Please select files first.');
    }
}

function testButtonClick() {
    alert('Button click test works! JavaScript is functioning.');
}

function testUploadEndpoint() {
    fetch('/articles/upload-pdf/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({test: 'data'})
    })
    .then(response => response.text())
    .then(text => {
        alert(`Upload endpoint test: Status ${response.status}\nResponse: ${text.substring(0, 100)}`);
    })
    .catch(error => {
        alert(`Upload endpoint failed: ${error.message}`);
    });
}

function debounceSearch() {
    clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(performSearch, 300);
}

function performSearch() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filterType = document.getElementById('filterType').value;
    const fileRows = document.querySelectorAll('.file-row');
    
    fileRows.forEach(row => {
        const fileName = row.querySelector('.file-name').textContent.toLowerCase();
        const fileType = row.dataset.fileType;
        
        let shouldShow = true;
        
        if (searchTerm) {
            shouldShow = fileName.includes(searchTerm);
        }
        
        if (filterType !== 'all' && shouldShow) {
            if (filterType === 'pdf') {
                shouldShow = fileType === 'pdf';
            } else if (filterType === 'article') {
                shouldShow = fileType === 'article';
            }
        }
        
        row.style.display = shouldShow ? '' : 'none';
    });
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('filterType').value = 'all';
    const fileRows = document.querySelectorAll('.file-row');
    fileRows.forEach(row => {
        row.style.display = '';
    });
}

function showExtractedText(text, fileName) {
    const modalElement = document.getElementById('extractedTextModal');
    const modalTitle = modalElement.querySelector('.modal-title');
    const modalBody = modalElement.querySelector('.modal-body');
    
    modalTitle.textContent = `Extracted Text: ${fileName}`;
    modalBody.innerHTML = `<pre style="white-space: pre-wrap; max-height: 400px; overflow-y: auto;">${text}</pre>`;
    
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

function deletePDFFile(fileId, fileName) {
    if (!confirm(`Are you sure you want to delete "${fileName}"?`)) {
        return;
    }
    
    fetch(`/articles/delete-pdf/${fileId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', `File "${fileName}" deleted successfully!`);
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showAlert('danger', `Error deleting file: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', `Error deleting file: ${error.message}`);
    });
}

function showFileInfo(articleId) {
    fetch(`/articles/get-file-info/${articleId}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const modalElement = document.getElementById('fileInfoModal');
            const modalTitle = modalElement.querySelector('.modal-title');
            const modalBody = modalElement.querySelector('.modal-body');
            
            modalTitle.textContent = `File Information: ${data.filename}`;
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>File Details:</h6>
                        <ul class="list-unstyled">
                            <li><strong>Filename:</strong> ${data.filename}</li>
                            <li><strong>Size:</strong> ${data.size}</li>
                            <li><strong>Upload Date:</strong> ${data.upload_date}</li>
                            <li><strong>Status:</strong> ${data.status}</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6>Google Drive Info:</h6>
                        <ul class="list-unstyled">
                            <li><strong>File ID:</strong> ${data.google_drive_file_id || 'N/A'}</li>
                            <li><strong>Web View:</strong> <a href="${data.google_drive_web_view_link}" target="_blank">Open in Google Drive</a></li>
                        </ul>
                    </div>
                </div>
            `;
            
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        } else {
            showAlert('danger', `Error getting file info: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', `Error getting file info: ${error.message}`);
    });
}

function deleteFile(articleId, fileName) {
    if (!confirm(`Are you sure you want to delete "${fileName}"?`)) {
        return;
    }
    
    fetch(`/articles/delete-file/${articleId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', `File "${fileName}" deleted successfully!`);
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showAlert('danger', `Error deleting file: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', `Error deleting file: ${error.message}`);
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('pdfFileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const testUploadBtn = document.getElementById('testUploadBtn');
    const testButtonClickBtn = document.getElementById('testButtonClickBtn');
    const testUploadEndpointBtn = document.getElementById('testUploadEndpointBtn');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const searchInput = document.getElementById('searchInput');
    const filterType = document.getElementById('filterType');
    
    if (!fileInput || !uploadBtn) {
        console.error('Required elements not found');
        console.error('fileInput:', fileInput);
        console.error('uploadBtn:', uploadBtn);
        return;
    }
    
    console.log('File manager JavaScript loaded successfully');
    console.log('Upload button found:', uploadBtn);
    
    // File selection handler
    fileInput.addEventListener('change', function() {
        const files = this.files;
        if (files.length > 0) {
            uploadBtn.innerHTML = `<i class="fas fa-cloud-upload-alt"></i> Upload ${files.length} File(s) to Google Drive`;
            uploadBtn.classList.remove('btn-secondary');
            uploadBtn.classList.add('btn-success');
        } else {
            uploadBtn.innerHTML = `<i class="fas fa-cloud-upload-alt"></i> Save & Upload to Google Drive`;
            uploadBtn.classList.remove('btn-success');
            uploadBtn.classList.add('btn-secondary');
        }
    });
    
    // Button click handlers
    uploadBtn.addEventListener('click', handleUploadClick);
    
    if (testUploadBtn) {
        testUploadBtn.addEventListener('click', testUpload);
    }
    if (testButtonClickBtn) {
        testButtonClickBtn.addEventListener('click', testButtonClick);
    }
    if (testUploadEndpointBtn) {
        testUploadEndpointBtn.addEventListener('click', testUploadEndpoint);
    }
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', clearSearch);
    }
    
    // Search handlers
    if (searchInput) {
        searchInput.addEventListener('input', debounceSearch);
    }
    if (filterType) {
        filterType.addEventListener('change', performSearch);
    }
});