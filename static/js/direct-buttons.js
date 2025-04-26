/**
 * JavaScript مبسط جداً لتفعيل أزرار الإجراءات في صفحة الأرشيف
 */

// استدعاء الدالة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف direct-buttons.js');
    
    // الانتظار قليلاً لضمان تحميل جميع العناصر
    setTimeout(initializeArchiveButtons, 500);
});

/**
 * تهيئة أزرار الأرشيف وربط أحداث النقر
 */
function initializeArchiveButtons() {
    console.log('تهيئة أزرار الأرشيف...');
    
    // متغيرات عامة
    window.selectedItemId = null;
    window.selectedItemType = null;
    
    // ربط أحداث النقر على المجلدات
    var folders = document.querySelectorAll('.folder-item');
    folders.forEach(function(folder) {
        folder.onclick = function(event) {
            // السماح للرابط بالعمل إذا تم النقر عليه مباشرة
            if (event.target.tagName === 'A' || event.target.closest('a')) {
                return true;
            }
            
            event.preventDefault();
            event.stopPropagation();
            
            // إلغاء تحديد العناصر الأخرى
            clearSelection();
            
            // تحديد هذا المجلد
            this.style.backgroundColor = 'rgba(13, 110, 253, 0.1)';
            this.style.border = '2px solid #0d6efd';
            
            // حفظ معلومات العنصر المحدد
            window.selectedItemId = this.getAttribute('data-folder-id');
            window.selectedItemType = 'folder';
            
            console.log('تم تحديد مجلد:', window.selectedItemId);
            
            // تفعيل الأزرار
            document.getElementById('edit-btn').disabled = false;
            document.getElementById('delete-btn').disabled = false;
            document.getElementById('export-btn').disabled = true; // لا يمكن تصدير المجلدات
        };
    });
    
    // ربط أحداث النقر على الملفات
    var files = document.querySelectorAll('.file-item');
    files.forEach(function(file) {
        file.onclick = function(event) {
            // السماح للرابط بالعمل إذا تم النقر عليه مباشرة
            if (event.target.tagName === 'A' || event.target.closest('a')) {
                return true;
            }
            
            event.preventDefault();
            event.stopPropagation();
            
            // إلغاء تحديد العناصر الأخرى
            clearSelection();
            
            // تحديد هذا الملف
            this.style.backgroundColor = 'rgba(13, 110, 253, 0.1)';
            this.style.border = '2px solid #0d6efd';
            
            // حفظ معلومات العنصر المحدد
            window.selectedItemId = this.getAttribute('data-file-id');
            window.selectedItemType = 'file';
            
            console.log('تم تحديد ملف:', window.selectedItemId);
            
            // تفعيل الأزرار
            document.getElementById('edit-btn').disabled = false;
            document.getElementById('delete-btn').disabled = false;
            document.getElementById('export-btn').disabled = false;
        };
    });
    
    // النقر على الخلفية لإلغاء التحديد
    var filesGrid = document.querySelector('.files-grid');
    if (filesGrid) {
        filesGrid.addEventListener('click', function(event) {
            if (event.target === this) {
                clearSelection();
            }
        });
    }
    
    // ربط أحداث النقر على الأزرار
    var editBtn = document.getElementById('edit-btn');
    var deleteBtn = document.getElementById('delete-btn');
    var exportBtn = document.getElementById('export-btn');
    
    if (editBtn) {
        editBtn.onclick = handleEditClick;
    }
    
    if (deleteBtn) {
        deleteBtn.onclick = handleDeleteClick;
    }
    
    if (exportBtn) {
        exportBtn.onclick = handleExportClick;
    }
    
    console.log('تم ربط أحداث الأزرار بنجاح');
}

/**
 * إلغاء تحديد جميع العناصر
 */
function clearSelection() {
    // إلغاء تحديد جميع العناصر
    var allItems = document.querySelectorAll('.folder-item, .file-item');
    allItems.forEach(function(item) {
        item.style.backgroundColor = '';
        item.style.border = '';
    });
    
    // إعادة تعيين المتغيرات العامة
    window.selectedItemId = null;
    window.selectedItemType = null;
    
    // تعطيل الأزرار
    document.getElementById('edit-btn').disabled = true;
    document.getElementById('delete-btn').disabled = true;
    document.getElementById('export-btn').disabled = true;
}

/**
 * معالجة النقر على زر التحرير
 */
function handleEditClick(event) {
    console.log('تم النقر على زر التحرير');
    
    // التحقق من وجود عنصر محدد
    if (!window.selectedItemId) {
        alert('الرجاء تحديد عنصر للتحرير أولاً');
        return false;
    }
    
    // اعتماداً على نوع العنصر المحدد، عرض النافذة المنبثقة المناسبة
    if (window.selectedItemType === 'folder') {
        // العثور على اسم المجلد
        var folderElement = document.querySelector('.folder-item[data-folder-id="' + window.selectedItemId + '"]');
        var folderName = folderElement.querySelector('.folder-name').textContent.trim();
        
        // تعيين قيم النموذج
        document.getElementById('edit-folder-id').value = window.selectedItemId;
        document.getElementById('edit-folder-name').value = folderName;
        
        // عرض النافذة المنبثقة
        var editFolderModal = new bootstrap.Modal(document.getElementById('editFolderModal'));
        editFolderModal.show();
    } else if (window.selectedItemType === 'file') {
        // العثور على اسم الملف
        var fileElement = document.querySelector('.file-item[data-file-id="' + window.selectedItemId + '"]');
        var fileName = fileElement.querySelector('.file-name').textContent.trim();
        
        // تعيين قيم النموذج
        document.getElementById('edit-file-id').value = window.selectedItemId;
        document.getElementById('edit-file-title').value = fileName;
        
        // عرض النافذة المنبثقة
        var editFileModal = new bootstrap.Modal(document.getElementById('editFileModal'));
        editFileModal.show();
    }
    
    return false;
}

/**
 * معالجة النقر على زر الحذف
 */
function handleDeleteClick(event) {
    console.log('تم النقر على زر الحذف');
    
    // التحقق من وجود عنصر محدد
    if (!window.selectedItemId) {
        alert('الرجاء تحديد عنصر للحذف أولاً');
        return false;
    }
    
    // اعتماداً على نوع العنصر المحدد، عرض النافذة المنبثقة المناسبة
    if (window.selectedItemType === 'folder') {
        // العثور على اسم المجلد
        var folderElement = document.querySelector('.folder-item[data-folder-id="' + window.selectedItemId + '"]');
        var folderName = folderElement.querySelector('.folder-name').textContent.trim();
        
        // تعيين قيم النموذج
        document.getElementById('delete-folder-id').value = window.selectedItemId;
        document.getElementById('delete-folder-name').textContent = folderName;
        
        // عرض النافذة المنبثقة
        var deleteFolderModal = new bootstrap.Modal(document.getElementById('deleteFolderModal'));
        deleteFolderModal.show();
    } else if (window.selectedItemType === 'file') {
        // العثور على اسم الملف
        var fileElement = document.querySelector('.file-item[data-file-id="' + window.selectedItemId + '"]');
        var fileName = fileElement.querySelector('.file-name').textContent.trim();
        
        // تعيين قيم النموذج
        document.getElementById('delete-file-id').value = window.selectedItemId;
        document.getElementById('delete-file-name').textContent = fileName;
        
        // عرض النافذة المنبثقة
        var deleteFileModal = new bootstrap.Modal(document.getElementById('deleteFileModal'));
        deleteFileModal.show();
    }
    
    return false;
}

/**
 * معالجة النقر على زر التصدير
 */
function handleExportClick(event) {
    console.log('تم النقر على زر التصدير');
    
    // التحقق من وجود عنصر محدد
    if (!window.selectedItemId) {
        alert('الرجاء تحديد ملف للتصدير أولاً');
        return false;
    }
    
    // التحقق من أن العنصر المحدد هو ملف
    if (window.selectedItemType !== 'file') {
        alert('يمكن تصدير الملفات فقط');
        return false;
    }
    
    // فتح رابط التنزيل
    window.open('/admin/download-document/' + window.selectedItemId + '/', '_blank');
    
    return false;
}