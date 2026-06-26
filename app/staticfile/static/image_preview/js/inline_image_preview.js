
(function() {
    'use strict';


    const CONFIG = {
        maxWidth: 250,
        maxHeight: 250,
        allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml'],
        debug: false
    };


    function log(...args) {
        if (CONFIG.debug) {
            console.log('[Inline Image Preview]', ...args);
        }
    }


    document.addEventListener('DOMContentLoaded', function() {
        setupInlineImagePreview();
        setupDynamicFormsetHandling();
    });

    function setupInlineImagePreview() {

        const inlineInputs = document.querySelectorAll('tr.form-row input[type="file"]');

        log(`Found ${inlineInputs.length} inline file inputs`);

        inlineInputs.forEach(function(input) {

            if (input.name && input.name.includes('__prefix__')) {
                log('Skipping template input:', input.name);
                return;
            }


            if (input.dataset.inlinePreviewSetup === 'true') {
                log('Already setup:', input.name);
                return;
            }

            setupSingleInlineInput(input);
        });
    }

    function setupSingleInlineInput(input) {
        log('Setting up inline input:', input.name);


        input.dataset.inlinePreviewSetup = 'true';


        const currentImageUrl = findCurrentImageUrlInline(input);
        log('Current image URL:', currentImageUrl);


        const previewContainer = createInlinePreviewContainer();


        const inputTd = input.closest('td');
        if (inputTd) {
            insertPreviewInTable(inputTd, previewContainer);
        } else {
            log('Could not find parent td for input:', input.name);
            return;
        }


        if (currentImageUrl) {
            showCurrentImageInline(previewContainer, currentImageUrl);
        } else {
            showNoImageInline(previewContainer);
        }


        input.addEventListener('change', function(event) {
            handleInlineFileChange(event, previewContainer, currentImageUrl);
        });

        log('Inline setup completed for:', input.name);
    }

    function insertPreviewInTable(inputTd, previewContainer) {

        const tr = inputTd.closest('tr');
        const newTr = document.createElement('tr');
        newTr.className = 'inline-preview-row';

        const newTd = document.createElement('td');
        newTd.colSpan = tr.children.length;
        newTd.appendChild(previewContainer);

        newTr.appendChild(newTd);


        tr.parentNode.insertBefore(newTr, tr.nextSibling);
    }

    function findCurrentImageUrlInline(input) {

        const inputTd = input.closest('td');
        if (inputTd) {
            const fileUploadP = inputTd.querySelector('.file-upload');
            if (fileUploadP) {
                const link = fileUploadP.querySelector('a[href]');
                if (link && isImageUrl(link.href)) {
                    return link.href;
                }
            }
        }


        const tr = input.closest('tr');
        if (tr) {
            const link = tr.querySelector('a[href]');
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

    function createInlinePreviewContainer() {
        const container = document.createElement('div');
        container.className = 'inline-image-preview';
        return container;
    }

    function showCurrentImageInline(container, imageUrl) {
        container.className = 'inline-image-preview has-current';
        container.dataset.originalImage = imageUrl;

        const fileName = getFileName(imageUrl);


        const testImg = new Image();
        testImg.onload = function() {
            container.innerHTML = `
                <div class="inline-preview-content">
                    <div class="inline-preview-header">현재 저장된 이미지:</div>
                    <div class="inline-preview-image-wrapper">
                        <img src="${imageUrl}" 
                             alt="현재 이미지" 
                             class="inline-preview-image"
                             style="max-width: ${CONFIG.maxWidth}px; max-height: ${CONFIG.maxHeight}px;">
                    </div>
                    <div class="inline-preview-info">파일: ${fileName}</div>
                    <button type="button" class="inline-preview-reset-btn" onclick="resetInlineImagePreview(this)">
                        원본으로 되돌리기
                    </button>
                </div>
            `;
        };
        testImg.onerror = function() {
            log('Failed to load inline image:', imageUrl);
            showNoImageInline(container);
        };
        testImg.src = imageUrl;
    }

    function showNoImageInline(container) {
        container.className = 'inline-image-preview no-image';
        container.innerHTML = `
            <div class="inline-preview-content">
                <div class="inline-preview-header">이미지 없음</div>
                <div class="inline-preview-placeholder" style="max-width: ${CONFIG.maxWidth}px;">
                    <span>No Image</span>
                </div>
            </div>
        `;
    }

    function showNewImageInline(container, file, originalImageUrl) {
        container.className = 'inline-image-preview has-new';

        const reader = new FileReader();
        reader.onload = function(e) {
            const fileSize = Math.round(file.size / 1024);

            let html = `
                <div class="inline-preview-content">
                    <div class="inline-preview-header">새로 선택된 이미지:</div>
                    <div class="inline-preview-image-wrapper">
                        <img src="${e.target.result}" 
                             alt="새 이미지 미리보기" 
                             class="inline-preview-image"
                             style="max-width: ${CONFIG.maxWidth}px; max-height: ${CONFIG.maxHeight}px;">
                    </div>
                    <div class="inline-preview-info">새 파일: ${file.name} (${fileSize}KB)</div>
            `;

            if (originalImageUrl) {
                html += '<div class="inline-preview-warning">기존 파일이 대체됩니다.</div>';
            }

            html += `
                    <button type="button" class="inline-preview-reset-btn" onclick="resetInlineImagePreview(this)">
                        원본으로 되돌리기
                    </button>
                </div>
            `;

            container.innerHTML = html;
        };
        reader.readAsDataURL(file);
    }

    function handleInlineFileChange(event, container, originalImageUrl) {
        const file = event.target.files[0];

        if (file) {

            if (CONFIG.allowedTypes.includes(file.type)) {
                log('Valid inline image file selected:', file.name);
                showNewImageInline(container, file, originalImageUrl);
            } else {
                log('Invalid file type:', file.type);
                alert('이미지 파일만 선택할 수 있습니다.');
                event.target.value = '';


                if (originalImageUrl) {
                    showCurrentImageInline(container, originalImageUrl);
                } else {
                    showNoImageInline(container);
                }
            }
        } else {

            log('Inline file selection canceled');
            if (originalImageUrl) {
                showCurrentImageInline(container, originalImageUrl);
            } else {
                showNoImageInline(container);
            }
        }
    }

    function setupDynamicFormsetHandling() {

        document.addEventListener('formset:added', function(event) {
            log('New formset row added:', event.detail);


            const newRow = event.target;
            const newInput = newRow.querySelector('input[type="file"]');

            if (newInput && !newInput.dataset.inlinePreviewSetup) {
                log('Setting up preview for new formset row');
                setupSingleInlineInput(newInput);
            }
        });


        document.addEventListener('formset:removed', function(event) {
            log('Formset row removed');
            const removedRow = event.target;
            const previewRow = removedRow.nextElementSibling;

            if (previewRow && previewRow.classList.contains('inline-preview-row')) {
                previewRow.remove();
            }
        });


        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE &&
                        node.tagName === 'TR' &&
                        node.classList.contains('form-row') &&
                        !node.classList.contains('empty-form')) {

                        const input = node.querySelector('input[type="file"]');
                        if (input && !input.dataset.inlinePreviewSetup) {
                            log('MutationObserver detected new input');

                            setTimeout(() => setupSingleInlineInput(input), 100);
                        }
                    }
                });
            });
        });


        const inlineContainers = document.querySelectorAll('.js-inline-admin-formset');
        inlineContainers.forEach(container => {
            observer.observe(container, { childList: true, subtree: true });
        });
    }

    function getFileName(url) {
        return url.split('/').pop().split('?')[0];
    }

    window.resetInlineImagePreview = function(button) {
        const container = button.closest('.inline-image-preview');
        const previewRow = container.closest('tr.inline-preview-row');
        const inputRow = previewRow.previousElementSibling;
        const input = inputRow.querySelector('input[type="file"]');
        const originalImageUrl = container.dataset.originalImage;


        input.value = '';


        if (originalImageUrl) {
            showCurrentImageInline(container, originalImageUrl);
        } else {
            showNoImageInline(container);
        }

        log('Inline reset to original for:', input.name);
    };

    window.updateInlineImagePreviewConfig = function(newConfig) {
        Object.assign(CONFIG, newConfig);
        log('Inline config updated:', CONFIG);
    };

})();