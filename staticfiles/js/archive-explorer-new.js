/**
 * أرشيف المستندات - وظائف جافاسكريبت للتفاعل مع واجهة الأرشيف على نمط ويندوز (النسخة الجديدة)
 */

// إنشاء فضاء أسماء للتطبيق لتجنب تداخل المتغيرات العامة
window.archiveApp = window.archiveApp || {
    // تتبع العناصر المحددة
    selectedItem: null,
    selectedItemType: null, // 'folder' أو 'file'
    
    // حالة التطبيق
    currentView: 'grid', // 'grid' أو 'list'
    
    // نظام التنبيهات
    notifications: {
        showAlert: function(message, type = 'info') {
            console.log(`تنبيه (${type}): ${message}`);
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show fixed-top m-3`;
            alertDiv.setAttribute('role', 'alert');
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            document.body.appendChild(alertDiv);
            
            // إخفاء التنبيه تلقائيًا بعد 3 ثوانٍ
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.classList.remove('show');
                    setTimeout(() => alertDiv.parentNode.removeChild(alertDiv), 150);
                }
            }, 3000);
        }
    },
    
    // تأثيرات بصرية
    effects: {
        // تأثير نبض للعناصر (مثل تأثير النقر)
        pulseElement: function(element) {
            if (!element) return;
            
            element.classList.add('pulse-effect');
            setTimeout(() => {
                element.classList.remove('pulse-effect');
            }, 300);
        },
        
        // إضافة تدرج لإظهار العناصر
        fadeInElement: function(element) {
            if (!element) return;
            
            element.style.opacity = '0';
            element.style.display = 'block';
            
            let opacity = 0;
            const fadeIn = setInterval(() => {
                if (opacity >= 1) {
                    clearInterval(fadeIn);
                }
                element.style.opacity = opacity.toString();
                opacity += 0.1;
            }, 20);
        }
    },
    
    // معالجة الأحداث
    handlers: {
        // معالجة النقر على ملف
        fileClick: function(event) {
            const fileItem = event.currentTarget;
            console.log('تم النقر على ملف:', fileItem);
            
            // إلغاء تحديد جميع العناصر
            archiveApp.deselectAllItems();
            
            // تمييز الملف المحدد بصريًا
            fileItem.classList.add('selected');
            
            // تخزين معلومات العنصر المحدد
            archiveApp.selectedItem = fileItem;
            archiveApp.selectedItemType = 'file';
            
            // تفعيل أزرار الإجراءات
            archiveApp.toggleActionButtons(true);
            
            // منع انتشار الحدث للعناصر الأخرى
            event.stopPropagation();
        },
        
        // معالجة النقر على مجلد
        folderClick: function(event) {
            const folderItem = event.currentTarget;
            console.log('تم النقر على مجلد:', folderItem);
            
            // إلغاء تحديد جميع العناصر
            archiveApp.deselectAllItems();
            
            // تمييز المجلد المحدد بصريًا
            folderItem.classList.add('selected');
            
            // تخزين معلومات العنصر المحدد
            archiveApp.selectedItem = folderItem;
            archiveApp.selectedItemType = 'folder';
            
            // تفعيل أزرار الإجراءات
            archiveApp.toggleActionButtons(true);
            
            // منع انتشار الحدث للعناصر الأخرى
            event.stopPropagation();
        },
        
        // معالجة النقر على الخلفية (إلغاء التحديد)
        backgroundClick: function(event) {
            // تحقق مما إذا كان النقر على الخلفية وليس على عنصر قابل للتحديد
            const isBackground = !event.target.closest('.file-item, .folder-item, button, a, input, .modal');
            
            if (isBackground) {
                console.log('النقر على الخلفية - إلغاء التحديد');
                archiveApp.deselectAllItems();
                archiveApp.toggleActionButtons(false);
            }
        },
        
        // معالجة النقر على زر التحرير
        editClick: function(event) {
            console.log('تم النقر على زر التحرير');
            
            if (!archiveApp.selectedItem) {
                archiveApp.notifications.showAlert('الرجاء تحديد عنصر للتحرير أولاً', 'warning');
                return false;
            }
            
            // الحصول على بيانات العنصر المحدد
            const itemId = archiveApp.selectedItem.getAttribute('data-file-id') || 
                          archiveApp.selectedItem.getAttribute('data-folder-id');
            const itemType = archiveApp.selectedItemType;
            const itemName = archiveApp.selectedItem.querySelector('.file-name, .folder-name').textContent;
            
            // إظهار تأثير النقر
            archiveApp.effects.pulseElement(event.currentTarget);
            
            // تحضير رسالة التنبيه
            let message = '';
            if (itemType === 'file') {
                message = `تحرير الملف: ${itemName} (معرف: ${itemId})`;
            } else {
                message = `تحرير المجلد: ${itemName} (معرف: ${itemId})`;
            }
            
            // عرض نافذة التحرير
            archiveApp.showEditDialog(itemType, itemId, itemName);
            
            // منع انتشار الحدث والسلوك الافتراضي
            event.preventDefault();
            event.stopPropagation();
            return false;
        },
        
        // معالجة النقر على زر الحذف
        deleteClick: function(event) {
            console.log('تم النقر على زر الحذف');
            
            if (!archiveApp.selectedItem) {
                archiveApp.notifications.showAlert('الرجاء تحديد عنصر للحذف أولاً', 'warning');
                return false;
            }
            
            // الحصول على بيانات العنصر المحدد
            const itemId = archiveApp.selectedItem.getAttribute('data-file-id') || 
                          archiveApp.selectedItem.getAttribute('data-folder-id');
            const itemType = archiveApp.selectedItemType;
            const itemName = archiveApp.selectedItem.querySelector('.file-name, .folder-name').textContent;
            
            // إظهار تأثير النقر
            archiveApp.effects.pulseElement(event.currentTarget);
            
            // عرض نافذة تأكيد الحذف
            archiveApp.showDeleteConfirmation(itemType, itemId, itemName);
            
            // منع انتشار الحدث والسلوك الافتراضي
            event.preventDefault();
            event.stopPropagation();
            return false;
        },
        
        // معالجة النقر على زر التصدير/التنزيل
        exportClick: function(event) {
            console.log('تم النقر على زر التصدير');
            
            if (!archiveApp.selectedItem) {
                archiveApp.notifications.showAlert('الرجاء تحديد ملف للتصدير أولاً', 'warning');
                return false;
            }
            
            // التحقق من أن العنصر المحدد هو ملف
            if (archiveApp.selectedItemType !== 'file') {
                archiveApp.notifications.showAlert('يمكن تصدير الملفات فقط', 'info');
                return false;
            }
            
            // الحصول على بيانات الملف
            const fileId = archiveApp.selectedItem.getAttribute('data-file-id');
            const fileName = archiveApp.selectedItem.querySelector('.file-name').textContent;
            
            // إظهار تأثير النقر
            archiveApp.effects.pulseElement(event.currentTarget);
            
            // تحضير رسالة التنبيه
            const message = `بدء تنزيل الملف: ${fileName}`;
            archiveApp.notifications.showAlert(message, 'success');
            
            // بدء التنزيل (عن طريق توجيه المستخدم إلى رابط التنزيل)
            const downloadUrl = `/admin/download-document/${fileId}/`;
            window.open(downloadUrl, '_blank');
            
            // منع انتشار الحدث والسلوك الافتراضي
            event.preventDefault();
            event.stopPropagation();
            return false;
        }
    },
    
    // وظائف مساعدة
    deselectAllItems: function() {
        // إلغاء تحديد جميع العناصر
        document.querySelectorAll('.file-item, .folder-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        // إعادة تعيين متغيرات التحديد
        this.selectedItem = null;
        this.selectedItemType = null;
    },
    
    // تفعيل/تعطيل أزرار الإجراءات
    toggleActionButtons: function(enabled) {
        // تعطيل/تفعيل أزرار الإجراءات
        const actionButtons = document.querySelectorAll('.action-btn');
        
        actionButtons.forEach(btn => {
            btn.disabled = !enabled;
            if (enabled) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    },
    
    // عرض نافذة التحرير
    showEditDialog: function(itemType, itemId, itemName) {
        // إنشاء نص العنوان للنافذة
        let title = '';
        if (itemType === 'file') {
            title = `تحرير خصائص الملف: ${itemName}`;
        } else {
            title = `تحرير خصائص المجلد: ${itemName}`;
        }
        
        // إنشاء محتوى النافذة
        let content = `
            <form id="edit-form">
                <div class="mb-3">
                    <label for="item-name" class="form-label">الاسم</label>
                    <input type="text" class="form-control" id="item-name" value="${itemName}">
                </div>
                
                <input type="hidden" id="item-id" value="${itemId}">
                <input type="hidden" id="item-type" value="${itemType}">
            </form>
        `;
        
        // إضافة حقول خاصة بالملفات
        if (itemType === 'file') {
            content += `
                <div class="mb-3">
                    <label class="form-label">نوع الملف</label>
                    <input type="text" class="form-control" disabled value="PDF Document">
                </div>
                
                <div class="mb-3">
                    <label class="form-label">تاريخ الإنشاء</label>
                    <input type="text" class="form-control" disabled value="25/04/2025">
                </div>
            `;
        }
        
        // تعيين عنوان وبيانات النافذة المنبثقة
        const modalTitle = document.getElementById('editModalLabel');
        const modalBody = document.getElementById('editModalBody');
        const saveButton = document.getElementById('editModalSaveBtn');
        
        if (modalTitle && modalBody) {
            modalTitle.textContent = title;
            modalBody.innerHTML = content;
            
            // إضافة معالج حدث لزر الحفظ
            if (saveButton) {
                saveButton.onclick = function() {
                    // استرجاع البيانات من النموذج
                    const newName = document.getElementById('item-name').value;
                    const id = document.getElementById('item-id').value;
                    const type = document.getElementById('item-type').value;
                    
                    // عرض تأكيد التحديث
                    let updateMessage = '';
                    if (type === 'file') {
                        updateMessage = `تم تحديث الملف "${itemName}" إلى "${newName}"`;
                    } else {
                        updateMessage = `تم تحديث المجلد "${itemName}" إلى "${newName}"`;
                    }
                    
                    // إرسال البيانات للخادم (هنا سنكتفي بعرض رسالة تأكيد)
                    archiveApp.notifications.showAlert(updateMessage, 'success');
                    
                    // إغلاق النافذة
                    bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
                };
            }
            
            // عرض النافذة المنبثقة
            const editModal = new bootstrap.Modal(document.getElementById('editModal'));
            editModal.show();
        } else {
            console.error('لم يتم العثور على عناصر النافذة المنبثقة');
        }
    },
    
    // عرض نافذة تأكيد الحذف
    showDeleteConfirmation: function(itemType, itemId, itemName) {
        // إنشاء نص العنوان للنافذة
        let title = '';
        let message = '';
        
        if (itemType === 'file') {
            title = `حذف ملف`;
            message = `هل أنت متأكد من حذف الملف "${itemName}"؟ لا يمكن التراجع عن هذه العملية.`;
        } else {
            title = `حذف مجلد`;
            message = `هل أنت متأكد من حذف المجلد "${itemName}" وجميع محتوياته؟ لا يمكن التراجع عن هذه العملية.`;
        }
        
        // تعيين عنوان وبيانات النافذة المنبثقة
        const modalTitle = document.getElementById('deleteModalLabel');
        const modalBody = document.getElementById('deleteModalBody');
        const confirmButton = document.getElementById('deleteModalConfirmBtn');
        
        if (modalTitle && modalBody && confirmButton) {
            modalTitle.textContent = title;
            modalBody.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${message}
                </div>
                
                <input type="hidden" id="delete-item-id" value="${itemId}">
                <input type="hidden" id="delete-item-type" value="${itemType}">
            `;
            
            // إضافة معالج حدث لزر التأكيد
            confirmButton.onclick = function() {
                // استرجاع البيانات من النموذج
                const id = document.getElementById('delete-item-id').value;
                const type = document.getElementById('delete-item-type').value;
                
                // عرض تأكيد الحذف
                let deleteMessage = '';
                if (type === 'file') {
                    deleteMessage = `تم حذف الملف "${itemName}" بنجاح`;
                } else {
                    deleteMessage = `تم حذف المجلد "${itemName}" وجميع محتوياته بنجاح`;
                }
                
                // إرسال البيانات للخادم (هنا سنكتفي بعرض رسالة تأكيد)
                archiveApp.notifications.showAlert(deleteMessage, 'success');
                
                // إزالة العنصر المحذوف من الواجهة (تحديث فوري)
                if (archiveApp.selectedItem) {
                    archiveApp.selectedItem.remove();
                    archiveApp.selectedItem = null;
                    archiveApp.selectedItemType = null;
                    archiveApp.toggleActionButtons(false);
                }
                
                // إغلاق النافذة
                bootstrap.Modal.getInstance(document.getElementById('deleteModal')).hide();
            };
            
            // عرض النافذة المنبثقة
            const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
            deleteModal.show();
        } else {
            console.error('لم يتم العثور على عناصر النافذة المنبثقة');
        }
    },
    
    // تهيئة التطبيق
    init: function() {
        console.log('تهيئة تطبيق الأرشيف...');
        
        // إضافة CSS الديناميكي
        this.injectStyles();
        
        // ربط معالجات الأحداث
        this.bindEvents();
        
        console.log('تم تهيئة تطبيق الأرشيف بنجاح');
    },
    
    // إضافة أنماط CSS ديناميكية
    injectStyles: function() {
        // إنشاء عنصر <style>
        const style = document.createElement('style');
        style.textContent = `
            /* أنماط تحديد العناصر */
            .file-item.selected, .folder-item.selected {
                background-color: rgba(13, 110, 253, 0.1);
                border: 2px solid #0d6efd;
                border-radius: 5px;
                box-shadow: 0 0 5px rgba(13, 110, 253, 0.5);
            }
            
            /* تأثير النبض */
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .pulse-effect {
                animation: pulse 0.3s ease-in-out;
            }
            
            /* تحسينات للأزرار */
            .action-btn:not(:disabled) {
                cursor: pointer;
                opacity: 1;
            }
            
            .action-btn:disabled {
                cursor: not-allowed;
                opacity: 0.5;
            }
            
            .action-btn.active {
                color: #0d6efd;
            }
            
            /* تحسينات للنقر */
            .file-item, .folder-item {
                transition: all 0.2s ease;
            }
            
            .file-item:hover, .folder-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }
            
            .file-name, .folder-name {
                margin-top: 5px;
                word-break: break-word;
            }
        `;
        
        // إضافة عنصر <style> إلى <head>
        document.head.appendChild(style);
    },
    
    // ربط معالجات الأحداث
    bindEvents: function() {
        console.log('ربط معالجات الأحداث...');
        
        // النقر على الخلفية (لإلغاء التحديد)
        document.addEventListener('click', this.handlers.backgroundClick);
        
        // ربط أحداث الملفات والمجلدات
        // سيتم ربط هذه الأحداث بعد تحميل المستند بالكامل
        document.addEventListener('DOMContentLoaded', () => {
            // ربط أحداث النقر على الملفات
            document.querySelectorAll('.file-item').forEach(fileItem => {
                fileItem.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    archiveApp.handlers.fileClick.call(this, e);
                });
            });
            
            // ربط أحداث النقر على المجلدات
            document.querySelectorAll('.folder-item').forEach(folderItem => {
                folderItem.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    archiveApp.handlers.folderClick.call(this, e);
                });
            });
            
            // أزرار الإجراءات
            const editBtn = document.getElementById('edit-btn');
            const deleteBtn = document.getElementById('delete-btn');
            const exportBtn = document.getElementById('export-btn');
            
            if (editBtn) {
                editBtn.addEventListener('click', archiveApp.handlers.editClick);
            } else {
                console.error('زر التحرير غير موجود');
            }
            
            if (deleteBtn) {
                deleteBtn.addEventListener('click', archiveApp.handlers.deleteClick);
            } else {
                console.error('زر الحذف غير موجود');
            }
            
            if (exportBtn) {
                exportBtn.addEventListener('click', archiveApp.handlers.exportClick);
            } else {
                console.error('زر التصدير غير موجود');
            }
            
            // تعطيل أزرار الإجراءات في البداية
            archiveApp.toggleActionButtons(false);
        });
        
        // إعادة ربط الأحداث عند تغيير المحتوى
        // هذه الوظيفة يمكن استدعاؤها بعد تحديث المحتوى عبر AJAX
        this.rebindEvents = function() {
            console.log('إعادة ربط الأحداث بعد تحديث المحتوى');
            
            // إعادة ربط أحداث النقر على الملفات
            document.querySelectorAll('.file-item').forEach(fileItem => {
                // إزالة المستمعين القديمة لتجنب التكرار
                fileItem.removeEventListener('click', archiveApp.handlers.fileClick);
                
                // إضافة مستمع جديد
                fileItem.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    archiveApp.handlers.fileClick.call(this, e);
                });
            });
            
            // إعادة ربط أحداث النقر على المجلدات
            document.querySelectorAll('.folder-item').forEach(folderItem => {
                // إزالة المستمعين القديمة لتجنب التكرار
                folderItem.removeEventListener('click', archiveApp.handlers.folderClick);
                
                // إضافة مستمع جديد
                folderItem.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    archiveApp.handlers.folderClick.call(this, e);
                });
            });
        };
    }
};

// تهيئة التطبيق عند تحميل المستند
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل المستند. بدء تهيئة تطبيق الأرشيف...');
    
    // تهيئة النوافذ المنبثقة إذا لم تكن موجودة
    if (!document.getElementById('editModal')) {
        createEditModal();
    }
    
    if (!document.getElementById('deleteModal')) {
        createDeleteModal();
    }
    
    // تهيئة التطبيق
    window.archiveApp.init();
});

// إنشاء نافذة التحرير المنبثقة إذا لم تكن موجودة
function createEditModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'editModal';
    modal.tabIndex = '-1';
    modal.setAttribute('aria-labelledby', 'editModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="editModalLabel">تحرير العنصر</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="editModalBody">
                    <!-- سيتم تعبئة المحتوى ديناميكيًا -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-primary" id="editModalSaveBtn">حفظ التغييرات</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// إنشاء نافذة تأكيد الحذف المنبثقة إذا لم تكن موجودة
function createDeleteModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'deleteModal';
    modal.tabIndex = '-1';
    modal.setAttribute('aria-labelledby', 'deleteModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="deleteModalLabel">تأكيد الحذف</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="deleteModalBody">
                    <!-- سيتم تعبئة المحتوى ديناميكيًا -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-danger" id="deleteModalConfirmBtn">تأكيد الحذف</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}