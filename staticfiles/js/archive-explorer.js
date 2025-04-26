/**
 * أرشيف المستندات - وظائف جافاسكريبت للتفاعل مع واجهة الأرشيف على نمط ويندوز
 */

// انتظار تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف archive-explorer.js');
    
    // تعريف المتغيرات العامة
    const DEFAULT_ITEMS = [
        { id: 1, name: 'رسوم (1)', type: 'folder' },
        { id: 2, name: 'حضور (2)', type: 'folder' },
        { id: 3, name: 'حسابات (3)', type: 'folder' },
        { id: 4, name: 'محفوظات (4)', type: 'folder' },
        { id: 5, name: 'توكيلات (5)', type: 'folder' },
        { id: 101, name: 'تقرير_مالي.pdf', type: 'file', fileType: 'pdf' },
        { id: 102, name: 'نموذج_توكيل.docx', type: 'file', fileType: 'doc' },
        { id: 103, name: 'جدول_الحضور.xlsx', type: 'file', fileType: 'xls' }
    ];
    
    // محتويات المجلدات
    const FOLDER_CONTENTS = {
        '1': [
            { id: 111, name: 'رسم_بياني_1.pdf', type: 'file', fileType: 'pdf' },
            { id: 112, name: 'رسم_بياني_2.pdf', type: 'file', fileType: 'pdf' }
        ],
        '2': [
            { id: 221, name: 'سجل_الحضور_ابريل.xlsx', type: 'file', fileType: 'xls' },
            { id: 222, name: 'سجل_الحضور_مارس.xlsx', type: 'file', fileType: 'xls' },
            { id: 223, name: 'تقرير_الحضور.docx', type: 'file', fileType: 'doc' }
        ],
        '3': [
            { id: 331, name: 'ميزانية_2025.xlsx', type: 'file', fileType: 'xls' },
            { id: 332, name: 'تقرير_مالي_سنوي.pdf', type: 'file', fileType: 'pdf' },
            { id: 333, name: 'فواتير_مارس.pdf', type: 'file', fileType: 'pdf' }
        ],
        '4': [
            { id: 441, name: 'أرشيف_2024.zip', type: 'file', fileType: 'zip' },
            { id: 442, name: 'سجلات_قديمة.pdf', type: 'file', fileType: 'pdf' }
        ],
        '5': [
            { id: 551, name: 'نموذج_توكيل_رسمي.docx', type: 'file', fileType: 'doc' },
            { id: 552, name: 'توكيل_محمد_احمد.pdf', type: 'file', fileType: 'pdf' },
            { id: 553, name: 'توكيل_خالد_محمود.pdf', type: 'file', fileType: 'pdf' },
            { id: 554, name: 'توكيل_عمر_سعيد.pdf', type: 'file', fileType: 'pdf' }
        ]
    };
    
    // تهيئة الأحداث
    initEvents();
    
    // عرض المحتوى الافتراضي عند بدء التشغيل
    showDefaultContent();
    
    // تهيئة الأحداث للمكونات المختلفة
    function initEvents() {
        // ===== النقر على عناصر الوصول السريع =====
        document.querySelectorAll('.quick-access-item').forEach(function(item) {
            item.addEventListener('click', function(e) {
                e.preventDefault(); // منع السلوك الافتراضي للرابط
                const folderId = this.getAttribute('data-folder-id');
                const folderName = this.querySelector('span').textContent;
                
                alert('تم النقر على المجلد: ' + folderName);
                
                console.log('الوصول السريع: النقر على ' + folderName + ' (معرف: ' + folderId + ')');
                showFolderContent(folderId, folderName);
            });
        });
        
        // ===== النقر على المجلدات في عرض الشبكة =====
        document.addEventListener('click', function(e) {
            const folderItem = e.target.closest('.folder-item');
            if (folderItem) {
                const folderId = folderItem.getAttribute('data-folder-id');
                const folderName = folderItem.querySelector('.folder-name').textContent;
                
                console.log('المجلدات: النقر على ' + folderName + ' (معرف: ' + folderId + ')');
                showFolderContent(folderId, folderName);
            }
        });
        
        // ===== النقر على الملفات =====
        document.addEventListener('click', function(e) {
            const fileItem = e.target.closest('.file-item');
            if (fileItem) {
                const fileId = fileItem.getAttribute('data-file-id');
                const fileName = fileItem.querySelector('.file-name').textContent;
                
                console.log('الملفات: النقر على ' + fileName + ' (معرف: ' + fileId + ')');
                showFilePreview(fileName);
            }
        });
        
        // ===== النقر على الملفات في عرض القائمة =====
        document.addEventListener('click', function(e) {
            const listRow = e.target.closest('tr[data-file-id]');
            if (listRow) {
                const fileId = listRow.getAttribute('data-file-id');
                const fileName = listRow.querySelector('span').textContent;
                
                console.log('قائمة الملفات: النقر على ' + fileName + ' (معرف: ' + fileId + ')');
                showFilePreview(fileName);
            }
        });
        
        // ===== النقر على المجلدات في عرض القائمة =====
        document.addEventListener('click', function(e) {
            const listRow = e.target.closest('tr[data-folder-id]');
            if (listRow) {
                const folderId = listRow.getAttribute('data-folder-id');
                const folderName = listRow.querySelector('span').textContent;
                
                console.log('قائمة المجلدات: النقر على ' + folderName + ' (معرف: ' + folderId + ')');
                showFolderContent(folderId, folderName);
            }
        });
        
        // ===== زر الرئيسية =====
        document.addEventListener('click', function(e) {
            if (e.target.closest('.address-text a')) {
                e.preventDefault();
                console.log('النقر على زر الرئيسية');
                showDefaultContent();
            }
        });
        
        // ===== أزرار تبديل العرض =====
        document.getElementById('grid-view-btn').addEventListener('click', function() {
            this.classList.add('active');
            document.getElementById('list-view-btn').classList.remove('active');
            document.getElementById('grid-view').style.display = 'grid';
            document.getElementById('list-view').style.display = 'none';
        });
        
        document.getElementById('list-view-btn').addEventListener('click', function() {
            this.classList.add('active');
            document.getElementById('grid-view-btn').classList.remove('active');
            document.getElementById('grid-view').style.display = 'none';
            document.getElementById('list-view').style.display = 'block';
        });
    }
    
    // عرض محتوى المجلد
    function showFolderContent(folderId, folderName) {
        // تحديث عنوان الصفحة
        updatePathDisplay(folderName);
        
        // تحديث حالة المجلدات (تمييز العنصر المحدد)
        updateFolderSelection(folderId);
        
        // عرض محتوى المجلد
        const contents = FOLDER_CONTENTS[folderId] || [];
        
        if (contents.length > 0) {
            renderContents(contents);
        } else {
            // إذا لم يكن هناك محتوى محدد، عرض رسالة فارغة
            renderEmptyFolder();
        }
    }
    
    // عرض المحتوى الافتراضي (الجذر)
    function showDefaultContent() {
        updatePathDisplay();
        renderContents(DEFAULT_ITEMS);
    }
    
    // تحديث عرض المسار
    function updatePathDisplay(folderName) {
        const addressBar = document.querySelector('.address-text');
        
        if (folderName) {
            addressBar.innerHTML = '<a href="#" class="text-decoration-none">الرئيسية</a>' + 
                                  '<span class="breadcrumb-separator">/</span>' + folderName;
        } else {
            addressBar.innerHTML = '<a href="#" class="text-decoration-none">الرئيسية</a>';
        }
    }
    
    // تحديث تحديد المجلد
    function updateFolderSelection(folderId) {
        // إزالة التحديد من كل المجلدات
        document.querySelectorAll('.folder-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        // تحديد المجلد الحالي
        const selectedFolder = document.querySelector(`.folder-item[data-folder-id="${folderId}"]`);
        if (selectedFolder) {
            selectedFolder.classList.add('selected');
        }
    }
    
    // عرض الملفات والمجلدات
    function renderContents(items) {
        // تحضير قوالب HTML
        let gridHtml = '';
        let listHtml = '';
        
        // إنشاء عرض الشبكة وعرض القائمة
        items.forEach(item => {
            if (item.type === 'folder') {
                // إضافة مجلد إلى عرض الشبكة
                gridHtml += `
                    <div class="folder-item" data-folder-id="${item.id}">
                        <div class="folder-icon">
                            <i class="fas fa-folder"></i>
                        </div>
                        <div class="folder-name">${item.name}</div>
                    </div>
                `;
                
                // إضافة مجلد إلى عرض القائمة
                listHtml += `
                    <tr data-folder-id="${item.id}">
                        <td>
                            <div class="file-cell">
                                <div class="file-list-icon folder">
                                    <i class="fas fa-folder"></i>
                                </div>
                                <span>${item.name}</span>
                            </div>
                        </td>
                        <td>مجلد ملفات</td>
                        <td>-</td>
                        <td>21/04/2025</td>
                    </tr>
                `;
            } else if (item.type === 'file') {
                // تحديد أيقونة وفئة الملف
                let iconClass = 'fa-file';
                let colorClass = '';
                
                if (item.fileType === 'pdf') {
                    iconClass = 'fa-file-pdf';
                    colorClass = 'pdf';
                } else if (item.fileType === 'doc') {
                    iconClass = 'fa-file-word';
                    colorClass = 'doc';
                } else if (item.fileType === 'xls') {
                    iconClass = 'fa-file-excel';
                    colorClass = 'xls';
                } else if (item.fileType === 'zip') {
                    iconClass = 'fa-file-archive';
                    colorClass = 'zip';
                }
                
                // إضافة ملف إلى عرض الشبكة
                gridHtml += `
                    <div class="file-item" data-file-id="${item.id}">
                        <div class="file-icon ${colorClass}">
                            <i class="fas ${iconClass}"></i>
                        </div>
                        <div class="file-name">${item.name}</div>
                    </div>
                `;
                
                // تحديد نوع الملف بالنص
                let fileTypeName = 'ملف';
                let fileSize = '1.2 MB';
                
                if (item.fileType === 'pdf') {
                    fileTypeName = 'ملف PDF';
                } else if (item.fileType === 'doc') {
                    fileTypeName = 'مستند Word';
                } else if (item.fileType === 'xls') {
                    fileTypeName = 'جدول Excel';
                } else if (item.fileType === 'zip') {
                    fileTypeName = 'ملف مضغوط';
                }
                
                // إضافة ملف إلى عرض القائمة
                listHtml += `
                    <tr data-file-id="${item.id}">
                        <td>
                            <div class="file-cell">
                                <div class="file-list-icon ${colorClass}">
                                    <i class="fas ${iconClass}"></i>
                                </div>
                                <span>${item.name}</span>
                            </div>
                        </td>
                        <td>${fileTypeName}</td>
                        <td>${fileSize}</td>
                        <td>21/04/2025</td>
                    </tr>
                `;
            }
        });
        
        // تحديث العرض
        document.getElementById('grid-view').innerHTML = gridHtml;
        document.getElementById('list-view').querySelector('tbody').innerHTML = listHtml;
        
        // تحديث عدد العناصر
        document.querySelector('.item-count').textContent = items.length + ' عنصر';
    }
    
    // عرض مجلد فارغ
    function renderEmptyFolder() {
        const emptyHtml = `
            <div class="text-center p-5">
                <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">هذا المجلد فارغ</h5>
            </div>
        `;
        
        document.getElementById('grid-view').innerHTML = emptyHtml;
        document.getElementById('list-view').querySelector('tbody').innerHTML = '';
        document.querySelector('.item-count').textContent = '0 عنصر';
    }
    
    // عرض معاينة الملف
    function showFilePreview(fileName) {
        // تحديد نوع الملف
        let fileType = 'مستند';
        let iconClass = 'fa-file';
        
        if (fileName.endsWith('.pdf')) {
            fileType = 'PDF';
            iconClass = 'fa-file-pdf';
        } else if (fileName.endsWith('.docx') || fileName.endsWith('.doc')) {
            fileType = 'Word';
            iconClass = 'fa-file-word';
        } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
            fileType = 'Excel';
            iconClass = 'fa-file-excel';
        } else if (fileName.endsWith('.zip')) {
            fileType = 'أرشيف مضغوط';
            iconClass = 'fa-file-archive';
        }
        
        // تعيين عنوان النافذة المنبثقة
        document.getElementById('previewModalLabel').textContent = fileName;
        
        // تعيين محتوى المعاينة
        document.getElementById('previewModalContent').innerHTML = `
            <div class="text-center py-5">
                <div class="mb-4">
                    <i class="fas ${iconClass} fa-4x"></i>
                </div>
                <h5>معاينة ${fileName}</h5>
                <p class="text-muted">جاري تحميل ملف ${fileType}...</p>
                <div class="progress mb-3">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 75%"></div>
                </div>
                <p class="small">سيتم فتح الملف في التطبيق المناسب عند اكتمال التحميل.</p>
            </div>
        `;
        
        // إظهار النافذة المنبثقة
        const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
        previewModal.show();
    }
});