/**
 * أرشيف المستندات - وظائف جافاسكريبت للتفاعل مع واجهة الأرشيف على نمط ويندوز (النسخة المُحسّنة)
 * تاريخ التحديث: 2025-04-26
 * الإصدار: 2.0
 */

// إنشاء فضاء أسماء للتطبيق لتجنب تداخل المتغيرات العامة
window.ArchiveExplorer = {
    // بيانات العنصر المحدد
    selected: {
        element: null,    // عنصر DOM المحدد
        id: null,         // معرف العنصر المحدد
        type: null,       // نوع العنصر (file/folder)
        name: null        // اسم العنصر المحدد
    },
    
    // وظائف التحديد
    selection: {
        // تحديد عنصر
        select: function(element) {
            // إلغاء التحديد أولاً
            this.clearSelection();
            
            // إذا كان عنصر صالح
            if (element) {
                console.log('⭐ تحديد عنصر:', element);
                
                // تمييز العنصر بصرياً
                element.classList.add('selected');
                
                // حفظ معلومات العنصر المحدد
                ArchiveExplorer.selected.element = element;
                
                // تحديد نوع العنصر (ملف أو مجلد)
                if (element.classList.contains('file-item')) {
                    ArchiveExplorer.selected.type = 'file';
                    ArchiveExplorer.selected.id = element.getAttribute('data-file-id');
                } else if (element.classList.contains('folder-item')) {
                    ArchiveExplorer.selected.type = 'folder';
                    ArchiveExplorer.selected.id = element.getAttribute('data-folder-id');
                }
                
                // حفظ اسم العنصر
                const nameElem = element.querySelector('.file-name, .folder-name');
                ArchiveExplorer.selected.name = nameElem ? nameElem.textContent.trim() : '';
                
                console.log('📌 معلومات العنصر المحدد:', {
                    id: ArchiveExplorer.selected.id,
                    type: ArchiveExplorer.selected.type,
                    name: ArchiveExplorer.selected.name
                });
                
                // تفعيل الأزرار
                ArchiveExplorer.buttons.enableActionButtons(true);
            } else {
                // إلغاء التحديد وتعطيل الأزرار
                ArchiveExplorer.buttons.enableActionButtons(false);
            }
        },
        
        // إلغاء التحديد
        clearSelection: function() {
            console.log('🔄 إلغاء التحديد');
            
            // إزالة تمييز جميع العناصر
            document.querySelectorAll('.file-item.selected, .folder-item.selected').forEach(item => {
                item.classList.remove('selected');
            });
            
            // إعادة تعيين معلومات التحديد
            ArchiveExplorer.selected.element = null;
            ArchiveExplorer.selected.id = null;
            ArchiveExplorer.selected.type = null;
            ArchiveExplorer.selected.name = null;
        }
    },
    
    // إدارة الأزرار
    buttons: {
        // تفعيل/تعطيل أزرار الإجراءات
        enableActionButtons: function(enable) {
            console.log((enable ? '✅ تفعيل' : '❌ تعطيل') + ' أزرار الإجراءات');
            
            // العثور على جميع أزرار الإجراءات
            const actionButtons = document.querySelectorAll('.action-btn');
            
            // تعيين حالة الأزرار
            actionButtons.forEach(button => {
                button.disabled = !enable;
                
                // إضافة/إزالة صنف "active" حسب الحالة
                if (enable) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            });
            
            // معالجة خاصة لزر التصدير (يعمل للملفات فقط)
            const exportBtn = document.getElementById('export-btn');
            if (exportBtn) {
                exportBtn.disabled = !enable || ArchiveExplorer.selected.type !== 'file';
            }
        }
    },
    
    // معالجات الأحداث
    handlers: {
        // معالجة النقر على زر التحرير
        handleEditClick: function(event) {
            console.log('🖋️ النقر على زر التحرير');
            
            // منع السلوك الافتراضي للمتصفح
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // التحقق من وجود عنصر محدد
            if (!ArchiveExplorer.selected.element) {
                alert('الرجاء تحديد عنصر للتحرير أولاً');
                return false;
            }
            
            // فتح النافذة المنبثقة المناسبة حسب نوع العنصر
            if (ArchiveExplorer.selected.type === 'folder') {
                // تحرير مجلد
                const folderNameInput = document.getElementById('edit-folder-name');
                const folderIdInput = document.getElementById('edit-folder-id');
                
                if (folderNameInput && folderIdInput) {
                    folderNameInput.value = ArchiveExplorer.selected.name;
                    folderIdInput.value = ArchiveExplorer.selected.id;
                    
                    // إظهار النافذة المنبثقة
                    const modal = new bootstrap.Modal(document.getElementById('editFolderModal'));
                    modal.show();
                } else {
                    console.error('⚠️ عناصر نافذة تحرير المجلد غير موجودة');
                }
            } else if (ArchiveExplorer.selected.type === 'file') {
                // تحرير ملف
                const fileTitleInput = document.getElementById('edit-file-title');
                const fileIdInput = document.getElementById('edit-file-id');
                
                if (fileTitleInput && fileIdInput) {
                    fileTitleInput.value = ArchiveExplorer.selected.name;
                    fileIdInput.value = ArchiveExplorer.selected.id;
                    
                    // إظهار النافذة المنبثقة
                    const modal = new bootstrap.Modal(document.getElementById('editFileModal'));
                    modal.show();
                } else {
                    console.error('⚠️ عناصر نافذة تحرير الملف غير موجودة');
                }
            }
            
            return false;
        },
        
        // معالجة النقر على زر الحذف
        handleDeleteClick: function(event) {
            console.log('🗑️ النقر على زر الحذف');
            
            // منع السلوك الافتراضي للمتصفح
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // التحقق من وجود عنصر محدد
            if (!ArchiveExplorer.selected.element) {
                alert('الرجاء تحديد عنصر للحذف أولاً');
                return false;
            }
            
            // فتح النافذة المنبثقة المناسبة حسب نوع العنصر
            if (ArchiveExplorer.selected.type === 'folder') {
                // حذف مجلد
                const folderIdInput = document.getElementById('delete-folder-id');
                const folderNameElem = document.getElementById('delete-folder-name');
                
                if (folderIdInput && folderNameElem) {
                    folderIdInput.value = ArchiveExplorer.selected.id;
                    folderNameElem.textContent = ArchiveExplorer.selected.name;
                    
                    // إظهار النافذة المنبثقة
                    const modal = new bootstrap.Modal(document.getElementById('deleteFolderModal'));
                    modal.show();
                } else {
                    console.error('⚠️ عناصر نافذة حذف المجلد غير موجودة');
                }
            } else if (ArchiveExplorer.selected.type === 'file') {
                // حذف ملف
                const fileIdInput = document.getElementById('delete-file-id');
                const fileNameElem = document.getElementById('delete-file-name');
                
                if (fileIdInput && fileNameElem) {
                    fileIdInput.value = ArchiveExplorer.selected.id;
                    fileNameElem.textContent = ArchiveExplorer.selected.name;
                    
                    // إظهار النافذة المنبثقة
                    const modal = new bootstrap.Modal(document.getElementById('deleteFileModal'));
                    modal.show();
                } else {
                    console.error('⚠️ عناصر نافذة حذف الملف غير موجودة');
                }
            }
            
            return false;
        },
        
        // معالجة النقر على زر التصدير
        handleExportClick: function(event) {
            console.log('📤 النقر على زر التصدير');
            
            // منع السلوك الافتراضي للمتصفح
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // التحقق من وجود عنصر محدد
            if (!ArchiveExplorer.selected.element) {
                alert('الرجاء تحديد ملف للتصدير أولاً');
                return false;
            }
            
            // التحقق من أن العنصر المحدد هو ملف
            if (ArchiveExplorer.selected.type !== 'file') {
                alert('يمكن تصدير الملفات فقط');
                return false;
            }
            
            // بدء تنزيل الملف
            const downloadUrl = `/admin/download-document/${ArchiveExplorer.selected.id}/`;
            console.log('📥 جاري تنزيل الملف:', downloadUrl);
            
            // فتح نافذة جديدة للتنزيل
            window.open(downloadUrl, '_blank');
            
            return false;
        },
        
        // معالجة النقر على ملف
        handleFileClick: function(event) {
            console.log('📄 النقر على ملف');
            
            // السماح للروابط بالعمل بشكل طبيعي
            if (event.target.tagName === 'A' || event.target.closest('a')) {
                return true;
            }
            
            // منع السلوك الافتراضي
            event.preventDefault();
            event.stopPropagation();
            
            // تحديد الملف
            ArchiveExplorer.selection.select(this);
            
            return false;
        },
        
        // معالجة النقر على مجلد
        handleFolderClick: function(event) {
            console.log('📁 النقر على مجلد');
            
            // السماح للروابط بالعمل بشكل طبيعي
            if (event.target.tagName === 'A' || event.target.closest('a')) {
                return true;
            }
            
            // منع السلوك الافتراضي
            event.preventDefault();
            event.stopPropagation();
            
            // تحديد المجلد
            ArchiveExplorer.selection.select(this);
            
            return false;
        },
        
        // معالجة النقر على الخلفية
        handleBackgroundClick: function(event) {
            // التحقق من أن النقر كان على الخلفية وليس على عنصر قابل للتحديد
            if (event.target.classList.contains('files-grid') || 
                event.target.classList.contains('explorer-container') ||
                event.target.classList.contains('content-view')) {
                console.log('🔳 النقر على الخلفية');
                
                // إلغاء التحديد
                ArchiveExplorer.selection.clearSelection();
                ArchiveExplorer.buttons.enableActionButtons(false);
            }
        }
    },
    
    // تهيئة التطبيق
    init: function() {
        console.log('🚀 تهيئة تطبيق الأرشيف...');
        
        // إضافة الأنماط الديناميكية
        this.injectStyles();
        
        // ربط أحداث العناصر
        this.bindEvents();
        
        // تعطيل أزرار الإجراءات في البداية
        this.buttons.enableActionButtons(false);
        
        console.log('✅ تم تهيئة تطبيق الأرشيف بنجاح');
    },
    
    // إضافة أنماط CSS ديناميكية
    injectStyles: function() {
        const style = document.createElement('style');
        style.textContent = `
            /* أنماط العناصر المحددة */
            .file-item.selected, .folder-item.selected {
                background-color: rgba(13, 110, 253, 0.1);
                border: 2px solid #0d6efd !important;
                box-shadow: 0 0 8px rgba(13, 110, 253, 0.5);
            }
            
            /* تأثير النبض للأزرار */
            @keyframes pulse-effect {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .action-btn:not(:disabled):active {
                animation: pulse-effect 0.3s ease-in-out;
            }
            
            /* تحسينات للأزرار */
            .action-btn {
                transition: all 0.2s ease;
            }
            
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
            
            /* تحسينات المجلدات والملفات */
            .file-item, .folder-item {
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                border: 2px solid transparent;
            }
            
            .file-item:hover, .folder-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }
            
            /* إصلاح مشكلة التراكب */
            .vertical-separator {
                z-index: 0;
            }
        `;
        
        document.head.appendChild(style);
    },
    
    // ربط أحداث العناصر
    bindEvents: function() {
        console.log('🔄 ربط أحداث العناصر...');
        
        // أزرار الإجراءات
        const editBtn = document.getElementById('edit-btn');
        const deleteBtn = document.getElementById('delete-btn');
        const exportBtn = document.getElementById('export-btn');
        
        if (editBtn) {
            editBtn.addEventListener('click', this.handlers.handleEditClick);
            console.log('✓ تم ربط زر التحرير');
        }
        
        if (deleteBtn) {
            deleteBtn.addEventListener('click', this.handlers.handleDeleteClick);
            console.log('✓ تم ربط زر الحذف');
        }
        
        if (exportBtn) {
            exportBtn.addEventListener('click', this.handlers.handleExportClick);
            console.log('✓ تم ربط زر التصدير');
        }
        
        // ربط أحداث النقر للملفات والمجلدات
        document.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', this.handlers.handleFileClick);
        });
        
        document.querySelectorAll('.folder-item').forEach(item => {
            item.addEventListener('click', this.handlers.handleFolderClick);
        });
        
        // ربط حدث النقر على الخلفية لإلغاء التحديد
        document.addEventListener('click', this.handlers.handleBackgroundClick);
    }
};

// دوال معالجة النقر على الأزرار (للاستخدام في الوسوم HTML)
function handleEditClick(event) {
    console.log('🔄 توجيه طلب التحرير إلى المعالج الرئيسي');
    if (window.ArchiveExplorer && window.ArchiveExplorer.handlers) {
        return window.ArchiveExplorer.handlers.handleEditClick(event);
    }
    alert('لم يتم تحميل معالج التحرير بعد');
    return false;
}

function handleDeleteClick(event) {
    console.log('🔄 توجيه طلب الحذف إلى المعالج الرئيسي');
    if (window.ArchiveExplorer && window.ArchiveExplorer.handlers) {
        return window.ArchiveExplorer.handlers.handleDeleteClick(event);
    }
    alert('لم يتم تحميل معالج الحذف بعد');
    return false;
}

function handleExportClick(event) {
    console.log('🔄 توجيه طلب التصدير إلى المعالج الرئيسي');
    if (window.ArchiveExplorer && window.ArchiveExplorer.handlers) {
        return window.ArchiveExplorer.handlers.handleExportClick(event);
    }
    alert('لم يتم تحميل معالج التصدير بعد');
    return false;
}

// تهيئة التطبيق عند تحميل المستند
document.addEventListener('DOMContentLoaded', function() {
    console.log('📃 تم تحميل المستند - بدء تهيئة تطبيق الأرشيف...'); 
    setTimeout(function() {
        window.ArchiveExplorer.init();
    }, 500); // تأخير قليل للتأكد من تحميل الصفحة بالكامل
});
