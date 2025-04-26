/**
 * وظائف معالجة أحداث الأزرار في واجهة الأرشيف الإلكتروني
 */

// وظيفة تعديل المجلد أو الملف المحدد
function handleEditClick() {
    console.log('وظيفة التعديل');
    if (selectedItemType === 'folder' && selectedFolderId) {
        // فتح نافذة تعديل المجلد
        $('#edit-folder-id').val(selectedFolderId);
        $('#edit-folder-name').val(selectedItemName);
        $('#editFolderModal').modal('show');
    } else if (selectedItemType === 'file' && selectedFileId) {
        // فتح نافذة تعديل الملف
        $('#edit-file-id').val(selectedFileId);
        $('#edit-file-title').val(selectedItemName);
        $('#editFileModal').modal('show');
    }
    return false;
}

// وظيفة حذف المجلد أو الملف المحدد
function handleDeleteClick() {
    console.log('وظيفة الحذف');
    if (selectedItemType === 'folder' && selectedFolderId) {
        // فتح نافذة حذف المجلد
        $('#delete-folder-id').val(selectedFolderId);
        $('#delete-folder-name').text(selectedItemName);
        $('#deleteFolderModal').modal('show');
    } else if (selectedItemType === 'file' && selectedFileId) {
        // فتح نافذة حذف الملف
        $('#delete-file-id').val(selectedFileId);
        $('#delete-file-name').text(selectedItemName);
        $('#deleteFileModal').modal('show');
    }
    return false;
}

// وظيفة تصدير (تنزيل) الملف المحدد
function handleExportClick() {
    console.log('وظيفة التصدير');
    if (selectedItemType === 'file' && selectedFileId) {
        // توجيه المتصفح إلى رابط عرض الملف
        var viewUrl = `/archive/view_document/${selectedFileId}/`;
        window.open(viewUrl, '_blank');
    }
    return false;
}

// متغيرات عامة للاستخدام في جميع أنحاء التطبيق
var selectedFileId = null;
var selectedFolderId = null;
var selectedItemName = "";
var selectedItemType = null;

// ربط الوظائف عند تحميل المستند
$(document).ready(function() {
    console.log('تم تحميل ملف archive-buttons.js');
});