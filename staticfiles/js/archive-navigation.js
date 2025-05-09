/**
 * وظائف متقدمة لتفعيل أزرار التنقل والإجراءات في صفحة الأرشيف الإلكتروني
 * تاريخ الإنشاء: 2025-04-26
 * الإصدار: 1.0
 */

// تأكيد تنفيذ الكود بعد تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف archive-navigation.js - إصدار 1.0');
    initArchiveButtons();
    initFolderItemsSelection();
    initFileItemsSelection();
    initNavigationHistory();
});

/**
 * تهيئة أزرار التنقل والإجراءات
 */
function initArchiveButtons() {
    console.log('تهيئة أزرار التنقل والإجراءات...');
    
    // المتغيرات العامة للتطبيق
    window.selectedItemId = null;
    window.selectedItemType = null;
    window.selectedItemElement = null;
    
    // ربط أزرار الإجراءات
    const editBtn = document.getElementById('edit-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const exportBtn = document.getElementById('export-btn');
    
    if (editBtn) {
        editBtn.onclick = handleEditClick;
        console.log('تم تفعيل زر التعديل');
    }
    
    if (deleteBtn) {
        deleteBtn.onclick = handleDeleteClick;
        console.log('تم تفعيل زر الحذف');
    }
    
    if (exportBtn) {
        exportBtn.onclick = handleExportClick;
        console.log('تم تفعيل زر التصدير');
    }
    
    // ربط أحداث النقر خارج العناصر لإلغاء التحديد
    document.addEventListener('click', function(event) {
        const filesGrid = document.querySelector('.files-grid');
        // التأكد من أن النقر كان على الخلفية وليس على عنصر قابل للتحديد
        if (event.target === filesGrid) {
            clearSelection();
        }
    });
    
    // بدء الأزرار معطلة في البداية
    disableActionButtons();
}

/**
 * تهيئة اختيار عناصر المجلدات
 */
function initFolderItemsSelection() {
    const folderItems = document.querySelectorAll('.folder-item');
    
    folderItems.forEach(function(folder) {
        folder.addEventListener('click', function(event) {
            // السماح للرابط بالعمل إذا كان النقر عليه مباشرة
            if (event.target.tagName === 'A' || event.target.closest('a')) {
                return true;
            }
            
            event.preventDefault();
            event.stopPropagation();
            
            // إلغاء التحديد السابق
            clearSelection();
            
            // تحديد هذا المجلد
            folder.classList.add('selected');
            
            // تخزين المعلومات
            window.selectedItemId = folder.getAttribute('data-folder-id');
            window.selectedItemType = 'folder';
            window.selectedItemElement = folder;
            
            // تفعيل الأزرار
            enableActionButtons('folder');
            
            console.log('تم تحديد المجلد:', window.selectedItemId);
        });
    });
}

/**
 * تهيئة اختيار عناصر الملفات
 */
function initFileItemsSelection() {
    const fileItems = document.querySelectorAll('.file-item');
    
    fileItems.forEach(function(file) {
        file.addEventListener('click', function(event) {
            // السماح للرابط بالعمل إذا كان النقر عليه مباشرة
            if (event.target.tagName === 'A' || event.target.closest('a')) {
                return true;
            }
            
            event.preventDefault();
            event.stopPropagation();
            
            // إلغاء التحديد السابق
            clearSelection();
            
            // تحديد هذا الملف
            file.classList.add('selected');
            
            // تخزين المعلومات
            window.selectedItemId = file.getAttribute('data-file-id');
            window.selectedItemType = 'file';
            window.selectedItemElement = file;
            
            // تفعيل الأزرار
            enableActionButtons('file');
            
            console.log('تم تحديد الملف:', window.selectedItemId);
        });
        
        // إضافة النقر المزدوج للملفات
        file.addEventListener('dblclick', function(event) {
            event.preventDefault();
            
            const fileId = file.getAttribute('data-file-id');
            if (fileId) {
                const viewUrl = `/ar/dashboard/archive/view/${fileId}/`;
                window.open(viewUrl, '_blank');
            }
        });
    });
}

/**
 * إلغاء تحديد جميع العناصر
 */
function clearSelection() {
    // إلغاء تحديد جميع العناصر
    document.querySelectorAll('.folder-item.selected, .file-item.selected').forEach(function(item) {
        item.classList.remove('selected');
    });
    
    // إعادة تعيين المتغيرات العامة
    window.selectedItemId = null;
    window.selectedItemType = null;
    window.selectedItemElement = null;
    
    // تعطيل الأزرار
    disableActionButtons();
}

/**
 * تفعيل أزرار الإجراءات حسب نوع العنصر المحدد
 */
function enableActionButtons(type) {
    // تفعيل الأزرار العامة
    document.getElementById('edit-btn').disabled = false;
    document.getElementById('delete-btn').disabled = false;
    
    // تفعيل زر التصدير للملفات فقط
    if (type === 'file') {
        document.getElementById('export-btn').disabled = false;
    } else {
        document.getElementById('export-btn').disabled = true;
    }
}

/**
 * تعطيل جميع أزرار الإجراءات
 */
function disableActionButtons() {
    document.getElementById('edit-btn').disabled = true;
    document.getElementById('delete-btn').disabled = true;
    document.getElementById('export-btn').disabled = true;
}

/**
 * تهيئة تاريخ التنقل وزر التحديث
 */
function initNavigationHistory() {
    // أزرار التنقل
    const backBtn = document.querySelector('.nav-btn[title*="عودة"]');
    const forwardBtn = document.querySelector('.nav-btn[title*="اذهب"]');
    const refreshBtn = document.querySelector('.nav-btn[title*="تحديث"]');
    
    // تفعيل أزرار التنقل في المتصفح
    if (backBtn) {
        backBtn.addEventListener('click', function(event) {
            event.preventDefault();
            window.history.back();
        });
        console.log('تم تفعيل زر الرجوع للخلف');
    }
    
    if (forwardBtn) {
        forwardBtn.addEventListener('click', function(event) {
            event.preventDefault();
            window.history.forward();
        });
        console.log('تم تفعيل زر الذهاب للأمام');
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function(event) {
            event.preventDefault();
            window.location.reload();
        });
        console.log('تم تفعيل زر التحديث');
    }
}

/**
 * معالجة النقر على زر التعديل
 */
function handleEditClick(event) {
    event.preventDefault();
    
    console.log('تم النقر على زر التعديل');
    
    // التحقق من وجود عنصر محدد
    if (!window.selectedItemId) {
        alert('الرجاء تحديد عنصر للتعديل أولاً');
        return false;
    }
    
    // التصرف حسب نوع العنصر المحدد
    if (window.selectedItemType === 'folder') {
        // العثور على عناصر نموذج تعديل المجلد
        const folderNameInput = document.getElementById('edit-folder-name');
        const folderIdInput = document.getElementById('edit-folder-id');
        
        if (folderNameInput && folderIdInput) {
            // العثور على اسم المجلد
            const folderName = window.selectedItemElement.querySelector('.folder-name').textContent.trim();
            
            // تعبئة النموذج
            folderNameInput.value = folderName;
            folderIdInput.value = window.selectedItemId;
            
            // عرض النافذة المنبثقة
            const editFolderModal = new bootstrap.Modal(document.getElementById('editFolderModal'));
            editFolderModal.show();
        } else {
            console.error('عناصر نموذج تعديل المجلد غير موجودة');
            alert('لا يمكن تعديل المجلد، النموذج غير موجود');
        }
    } else if (window.selectedItemType === 'file') {
        // العثور على عناصر نموذج تعديل الملف
        const fileTitleInput = document.getElementById('edit-file-title');
        const fileIdInput = document.getElementById('edit-file-id');
        
        if (fileTitleInput && fileIdInput) {
            // العثور على اسم الملف
            const fileName = window.selectedItemElement.querySelector('.file-name').textContent.trim();
            
            // تعبئة النموذج
            fileTitleInput.value = fileName;
            fileIdInput.value = window.selectedItemId;
            
            // عرض النافذة المنبثقة
            const editFileModal = new bootstrap.Modal(document.getElementById('editFileModal'));
            editFileModal.show();
        } else {
            console.error('عناصر نموذج تعديل الملف غير موجودة');
            alert('لا يمكن تعديل الملف، النموذج غير موجود');
        }
    }
    
    return false;
}

/**
 * معالجة النقر على زر الحذف
 */
function handleDeleteClick(event) {
    event.preventDefault();
    
    console.log('تم النقر على زر الحذف');
    
    // التحقق من وجود عنصر محدد
    if (!window.selectedItemId) {
        alert('الرجاء تحديد عنصر للحذف أولاً');
        return false;
    }
    
    // التصرف حسب نوع العنصر المحدد
    if (window.selectedItemType === 'folder') {
        // العثور على عناصر نموذج حذف المجلد
        const folderIdInput = document.getElementById('delete-folder-id');
        const folderNameSpan = document.getElementById('delete-folder-name');
        
        if (folderIdInput && folderNameSpan) {
            // العثور على اسم المجلد
            const folderName = window.selectedItemElement.querySelector('.folder-name').textContent.trim();
            
            // تعبئة النموذج
            folderIdInput.value = window.selectedItemId;
            folderNameSpan.textContent = folderName;
            
            // عرض النافذة المنبثقة
            const deleteFolderModal = new bootstrap.Modal(document.getElementById('deleteFolderModal'));
            deleteFolderModal.show();
        } else {
            console.error('عناصر نموذج حذف المجلد غير موجودة');
            alert('لا يمكن حذف المجلد، النموذج غير موجود');
        }
    } else if (window.selectedItemType === 'file') {
        // العثور على عناصر نموذج حذف الملف
        const fileIdInput = document.getElementById('delete-file-id');
        const fileNameSpan = document.getElementById('delete-file-name');
        
        if (fileIdInput && fileNameSpan) {
            // العثور على اسم الملف
            const fileName = window.selectedItemElement.querySelector('.file-name').textContent.trim();
            
            // تعبئة النموذج
            fileIdInput.value = window.selectedItemId;
            fileNameSpan.textContent = fileName;
            
            // عرض النافذة المنبثقة
            const deleteFileModal = new bootstrap.Modal(document.getElementById('deleteFileModal'));
            deleteFileModal.show();
        } else {
            console.error('عناصر نموذج حذف الملف غير موجودة');
            alert('لا يمكن حذف الملف، النموذج غير موجود');
        }
    }
    
    return false;
}

/**
 * معالجة النقر على زر التصدير
 */
function handleExportClick(event) {
    event.preventDefault();
    
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
    
    // فتح نافذة تنزيل الملف
    const downloadUrl = `/ar/dashboard/archive/download/${window.selectedItemId}/`;
    console.log('جاري تنزيل الملف:', downloadUrl);
    window.open(downloadUrl, '_blank');
    
    return false;
}