(function() {
    'use strict';

    const CONFIG = {
        maxWidth: 300,
        maxHeight: 300,
        allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml'],
        debug: false
    };

    function log(...args) {
        if (CONFIG.debug) {
            console.log('[Admin Image Preview]', ...args);
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        setupAdminImagePreview();
    });

    function setupAdminImagePreview() {
        const adminFileInputs = document.querySelectorAll('.form-row:not(tr) input[type="file"]');

        log(`Found ${adminFileInputs.length} admin file inputs`);

        adminFileInputs.forEach(function(input) {
            if (input.name && input.name.includes('__prefix__')) {
                log('Skipping template input:', input.name);
                return;
            }

            if (input.dataset.previewSetup === 'true') {
                log('Already setup:', input.name);
                return;
            }

            setupSingleInput(input);
        });
    }


    function setupSingleInput(input) {
        log('Setting up input:', input.name);

        input.dataset.previewSetup = 'true';

        const currentImageUrl = findCurrentImageUrl(input);
        log('Current image URL:', currentImageUrl);

        const previewContainer = createPreviewContainer();

        const fileUploadP = input.closest('.file-upload');
        if (fileUploadP) {
            fileUploadP.parentNode.insertBefore(previewContainer, fileUploadP.nextSibling);
        } else {
            input.parentNode.insertBefore(previewContainer, input.nextSibling);
        }

        if (currentImageUrl) {
            showCurrentImage(previewContainer, currentImageUrl);
        } else {
            showNoImage(previewContainer);
        }

        input.addEventListener('change', function(event) {
            handleFileChange(event, previewContainer, currentImageUrl);
        });

        log('Setup completed for:', input.name);
    }

    function findCurrentImageUrl(input) {
        const fileUploadP = input.closest('.file-upload');
        if (fileUploadP) {
            const link = fileUploadP.querySelector('a[href]');
            if (link && isImageUrl(link.href)) {
                return link.href;
            }
        }

        const formRow = input.closest('.form-row');
        if (formRow) {
            const link = formRow.querySelector('a[href]');
            if (link && isImageUrl(link.href)) {
                return link.href;
            }
        }

        return null;
    }

    function isImageUrl(url) {
        if (!url) return false;
        const imageExtensions = /\.(jpg|jpeg|png|gif|bmp|webp|svg)$/i;
        return imageExtensions.test(url);
    }

    function createPreviewContainer() {
        const container = document.createElement('div');
        container.className = 'admin-image-preview';
        return container;
    }

    function showCurrentImage(container, imageUrl) {
        container.className = 'admin-image-preview has-current';
        container.dataset.originalImage = imageUrl;

        const fileName = getFileName(imageUrl);


        const testImg = new Image();
        testImg.onload = function() {
            container.innerHTML = `
                <div class="preview-header">현재 저장된 이미지:</div>
                <div class="preview-image-wrapper">
                    <img src="${imageUrl}" 
                         alt="현재 이미지" 
                         class="preview-image"
                         style="max-width: ${CONFIG.maxWidth}px; max-height: ${CONFIG.maxHeight}px;">
                </div>
                <div class="preview-info">파일: ${fileName}</div>
                <button type="button" class="preview-reset-btn" onclick="resetImagePreview(this)">
                    원본으로 되돌리기
                </button>
            `;
        };
        testImg.onerror = function() {
            log('Failed to load image:', imageUrl);
            showNoImage(container);
        };
        testImg.src = imageUrl;
    }

    function showNoImage(container) {
        container.className = 'admin-image-preview no-image';
        container.innerHTML = `
            <div class="preview-header">이미지 없음</div>
            <div class="preview-placeholder" style="max-width: ${CONFIG.maxWidth}px;">
                <span>No Image</span>
            </div>
        `;
    }

    function showNewImage(container, file, originalImageUrl) {
        container.className = 'admin-image-preview has-new';

        const reader = new FileReader();
        reader.onload = function(e) {
            const fileSize = Math.round(file.size / 1024);

            let html = `
                <div class="preview-header">새로 선택된 이미지:</div>
                <div class="preview-image-wrapper">
                    <img src="${e.target.result}" 
                         alt="새 이미지 미리보기" 
                         class="preview-image"
                         style="max-width: ${CONFIG.maxWidth}px; max-height: ${CONFIG.maxHeight}px;">
                </div>
                <div class="preview-info">새 파일: ${file.name} (${fileSize}KB)</div>
            `;

            if (originalImageUrl) {
                html += '<div class="preview-warning">기존 파일이 대체됩니다.</div>';
            }

            html += `
                <button type="button" class="preview-reset-btn" onclick="resetImagePreview(this)">
                    원본으로 되돌리기
                </button>
            `;

            container.innerHTML = html;
        };
        reader.readAsDataURL(file);
    }

    function handleFileChange(event, container, originalImageUrl) {
        const file = event.target.files[0];

        if (file) {

            if (CONFIG.allowedTypes.includes(file.type)) {
                log('Valid image file selected:', file.name);
                showNewImage(container, file, originalImageUrl);
            } else {
                log('Invalid file type:', file.type);
                alert('이미지 파일만 선택할 수 있습니다.');
                event.target.value = '';


                if (originalImageUrl) {
                    showCurrentImage(container, originalImageUrl);
                } else {
                    showNoImage(container);
                }
            }
        } else {

            log('File selection canceled');
            if (originalImageUrl) {
                showCurrentImage(container, originalImageUrl);
            } else {
                showNoImage(container);
            }
        }
    }

    function getFileName(url) {
        return url.split('/').pop().split('?')[0];
    }

    window.resetImagePreview = function(button) {
        const container = button.closest('.admin-image-preview');
        const fileUploadP = container.previousElementSibling;
        const input = fileUploadP.querySelector('input[type="file"]');
        const originalImageUrl = container.dataset.originalImage;


        input.value = '';


        if (originalImageUrl) {
            showCurrentImage(container, originalImageUrl);
        } else {
            showNoImage(container);
        }

        log('Reset to original for:', input.name);
    };

    window.updateAdminImagePreviewConfig = function(newConfig) {
        Object.assign(CONFIG, newConfig);
        log('Config updated:', CONFIG);
    };

})();