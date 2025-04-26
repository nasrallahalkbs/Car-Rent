/**
 * ملف JavaScript مخصص لإصلاح أزرار التنقل وأزرار الإجراءات في صفحة الأرشيف
 * تاريخ: 2025-04-26
 */

// التأكد من تنفيذ الكود بعد تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف direct-fix.js - إصلاح مباشر لأزرار الأرشيف');
    
    // تفعيل أزرار التنقل
    setupNavigationButtons();
    
    // تفعيل أزرار الإجراءات
    setupActionButtons();
    
    // تفعيل اختيار العناصر
    setupItemSelection();
});

/**
 * تهيئة أزرار التنقل
 */
function setupNavigationButtons() {
    // الأزرار الرئيسية للتنقل
    document.querySelectorAll('.nav-btn').forEach(function(button) {
        button.addEventListener('click', function(e) {
            const action = this.getAttribute('data-action');
            
            if (action === 'back') {
                window.history.back();
            } else if (action === 'forward') {
                window.history.forward();
            } else if (action === 'refresh') {
                window.location.reload();
            }
            
            e.preventDefault();
            return false;
        });
    });
    
    console.log('تم تفعيل أزرار التنقل');
}

/**
 * تهيئة أزرار الإجراءات
 */
function setupActionButtons() {
    // أزرار الإجراءات
    const editButton = document.getElementById('edit-btn');
    const deleteButton = document.getElementById('delete-btn');
    const exportButton = document.getElementById('export-btn');
    
    // تعطيل الأزرار إفتراضياً
    if (editButton) editButton.disabled = true;
    if (deleteButton) deleteButton.disabled = true;
    if (exportButton) exportButton.disabled = true;
    
    // ربط الأحداث بالأزرار
    if (editButton) {
        editButton.addEventListener('click', function(e) {
            handleEditAction();
            e.preventDefault();
        });
    }
    
    if (deleteButton) {
        deleteButton.addEventListener('click', function(e) {
            handleDeleteAction();
            e.preventDefault();
        });
    }
    
    if (exportButton) {
        exportButton.addEventListener('click', function(e) {
            handleExportAction();
            e.preventDefault();
        });
    }
    
    console.log('تم تفعيل أزرار الإجراءات');
}

/**
 * تهيئة اختيار العناصر
 */
function setupItemSelection() {
    // المجلدات
    document.querySelectorAll('.folder-item').forEach(function(folderItem) {
        folderItem.addEventListener('click', function(e) {
            // السماح بالتنقل إذا تم النقر على الرابط
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return true;
            }
            
            // إلغاء جميع التحديدات السابقة
            clearAllSelections();
            
            // تحديد هذا المجلد
            this.classList.add('selected');
            
            // تخزين المعلومات في متغير عام
            window.selectedItem = {
                id: this.getAttribute('data-folder-id'),
                type: 'folder',
                element: this
            };
            
            // تفعيل الأزرار
            enableActionButtons('folder');
            
            e.preventDefault();
            e.stopPropagation();
        });
    });
    
    // الملفات
    document.querySelectorAll('.file-item').forEach(function(fileItem) {
        fileItem.addEventListener('click', function(e) {
            // السماح بالتنقل إذا تم النقر على الرابط
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return true;
            }
            
            // إلغاء جميع التحديدات السابقة
            clearAllSelections();
            
            // تحديد هذا الملف
            this.classList.add('selected');
            
            // تخزين المعلومات في متغير عام
            window.selectedItem = {
                id: this.getAttribute('data-file-id'),
                type: 'file',
                element: this
            };
            
            // تفعيل الأزرار
            enableActionButtons('file');
            
            e.preventDefault();
            e.stopPropagation();
        });
        
        // النقر المزدوج لعرض الملف
        fileItem.addEventListener('dblclick', function(e) {
            const fileId = this.getAttribute('data-file-id');
            if (fileId) {
                window.open(`/ar/dashboard/archive/view/${fileId}/`, '_blank');
            }
            
            e.preventDefault();
        });
    });
    
    // إلغاء التحديد عند النقر خارج العناصر
    document.addEventListener('click', function(e) {
        const isOutsideSelection = !e.target.closest('.folder-item, .file-item, .action-btn');
        if (isOutsideSelection) {
            clearAllSelections();
        }
    });
    
    console.log('تم تفعيل اختيار العناصر');
}

/**
 * تفعيل أزرار الإجراءات
 */
function enableActionButtons(type) {
    const editButton = document.getElementById('edit-btn');
    const deleteButton = document.getElementById('delete-btn');
    const exportButton = document.getElementById('export-btn');
    
    // تفعيل أزرار التعديل والحذف للجميع
    if (editButton) editButton.disabled = false;
    if (deleteButton) deleteButton.disabled = false;
    
    // تفعيل زر التصدير للملفات فقط
    if (exportButton) {
        exportButton.disabled = (type !== 'file');
    }
}

/**
 * إلغاء تحديد جميع العناصر
 */
function clearAllSelections() {
    // إلغاء التحديد البصري
    document.querySelectorAll('.folder-item.selected, .file-item.selected').forEach(function(element) {
        element.classList.remove('selected');
    });
    
    // إعادة تعيين المتغير العام
    window.selectedItem = null;
    
    // تعطيل الأزرار
    const editButton = document.getElementById('edit-btn');
    const deleteButton = document.getElementById('delete-btn');
    const exportButton = document.getElementById('export-btn');
    
    if (editButton) editButton.disabled = true;
    if (deleteButton) deleteButton.disabled = true;
    if (exportButton) exportButton.disabled = true;
}

/**
 * معالجة إجراء التعديل
 */
function handleEditAction() {
    if (!window.selectedItem) {
        alert('الرجاء تحديد عنصر للتعديل');
        return;
    }
    
    console.log('تنفيذ إجراء التعديل على:', window.selectedItem);
    
    // معالجة مختلفة حسب نوع العنصر
    if (window.selectedItem.type === 'folder') {
        // الحصول على معرف المجلد
        const folderId = window.selectedItem.id;
        const folderName = window.selectedItem.element.querySelector('.folder-name').textContent.trim();
        
        // ملء النموذج المنبثق
        const editFolderModal = document.getElementById('editFolderModal');
        if (editFolderModal) {
            const folderIdInput = editFolderModal.querySelector('input[name="folder_id"]');
            const folderNameInput = editFolderModal.querySelector('input[name="folder_name"]');
            
            if (folderIdInput && folderNameInput) {
                folderIdInput.value = folderId;
                folderNameInput.value = folderName;
                
                // عرض النافذة المنبثقة
                try {
                    var modal = new bootstrap.Modal(editFolderModal);
                    modal.show();
                } catch (error) {
                    console.error('خطأ في عرض النافذة المنبثقة:', error);
                    alert('سيتم توجيهك إلى صفحة تعديل المجلد');
                    window.location.href = `/ar/dashboard/archive/folder/edit/${folderId}/`;
                }
            } else {
                // الانتقال إلى صفحة التعديل
                window.location.href = `/ar/dashboard/archive/folder/edit/${folderId}/`;
            }
        } else {
            // الانتقال إلى صفحة التعديل
            window.location.href = `/ar/dashboard/archive/folder/edit/${folderId}/`;
        }
    } else if (window.selectedItem.type === 'file') {
        // الحصول على معرف الملف
        const fileId = window.selectedItem.id;
        
        // الانتقال إلى صفحة التعديل
        window.location.href = `/ar/dashboard/archive/edit/${fileId}/`;
    }
}

/**
 * معالجة إجراء الحذف
 */
function handleDeleteAction() {
    if (!window.selectedItem) {
        alert('الرجاء تحديد عنصر للحذف');
        return;
    }
    
    console.log('تنفيذ إجراء الحذف على:', window.selectedItem);
    
    // التأكيد على الحذف
    const confirmation = window.confirm('هل أنت متأكد من رغبتك في حذف هذا العنصر؟');
    if (!confirmation) {
        return;
    }
    
    // معالجة مختلفة حسب نوع العنصر
    if (window.selectedItem.type === 'folder') {
        // حذف المجلد
        const folderId = window.selectedItem.id;
        window.location.href = `/ar/dashboard/archive/folder/delete/${folderId}/`;
    } else if (window.selectedItem.type === 'file') {
        // حذف الملف
        const fileId = window.selectedItem.id;
        window.location.href = `/ar/dashboard/archive/delete/${fileId}/`;
    }
}

/**
 * معالجة إجراء التصدير
 */
function handleExportAction() {
    if (!window.selectedItem || window.selectedItem.type !== 'file') {
        alert('الرجاء تحديد ملف للتصدير');
        return;
    }
    
    console.log('تنفيذ إجراء التصدير على:', window.selectedItem);
    
    // تصدير الملف (تنزيل)
    const fileId = window.selectedItem.id;
    window.open(`/ar/dashboard/archive/download/${fileId}/`, '_blank');
}