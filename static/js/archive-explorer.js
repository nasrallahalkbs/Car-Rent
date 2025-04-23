/**
 * نظام أرشفة إلكتروني مشابه لمستكشف ويندوز
 * يتم استخدام هذا الملف لإضافة وظائف التفاعل مع مستكشف الملفات
 */

$(document).ready(function() {
    // ============= وظائف عرض المجلدات والملفات =============
    
    // عرض محتويات مجلد محدد
    window.showFolderContents = function(folderId) {
        // تنظيف معرف المجلد
        let realFolderId = folderId;
        if (folderId && typeof folderId === 'string' && folderId.startsWith('folder-')) {
            realFolderId = folderId.replace('folder-', '');
        }
        
        console.log(`عرض محتويات المجلد: ${folderId} (المعرف الحقيقي: ${realFolderId})`);
        
        // تحديث الواجهة لإظهار أن المجلد تم اختياره
        $('.folder-item').removeClass('selected');
        $(`.folder-item[data-folder-id="${folderId}"]`).addClass('selected');
        
        let filesHtml = '';
        let listHtml = '';
        let itemCount = 0;
        
        // إذا كان المجلد هو "رسوم" (رقم 1)، سنعرض ملفات PDF
        if (folderId === 'folder-1' || realFolderId === '1') {
            filesHtml = `
                <div class="file-item" data-file-id="file-1-1">
                    <div class="file-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="file-name">رسم_بياني_1.pdf</div>
                </div>
                <div class="file-item" data-file-id="file-1-2">
                    <div class="file-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="file-name">رسم_بياني_2.pdf</div>
                </div>
            `;
            
            listHtml = `
                <tr data-file-id="file-1-1">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span>رسم_بياني_1.pdf</span>
                        </div>
                    </td>
                    <td>ملف PDF</td>
                    <td>854 KB</td>
                    <td>21/04/2025</td>
                </tr>
                <tr data-file-id="file-1-2">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span>رسم_بياني_2.pdf</span>
                        </div>
                    </td>
                    <td>ملف PDF</td>
                    <td>1.1 MB</td>
                    <td>21/04/2025</td>
                </tr>
            `;
            
            itemCount = 2;
        }
        // إذا كان المجلد هو "حضور" (رقم 2)، سنعرض ملفات Excel
        else if (folderId === 'folder-2' || realFolderId === '2') {
            filesHtml = `
                <div class="file-item" data-file-id="file-2-1">
                    <div class="file-icon xls">
                        <i class="fas fa-file-excel"></i>
                    </div>
                    <div class="file-name">سجل_الحضور_ابريل.xlsx</div>
                </div>
                <div class="file-item" data-file-id="file-2-2">
                    <div class="file-icon xls">
                        <i class="fas fa-file-excel"></i>
                    </div>
                    <div class="file-name">سجل_الحضور_مارس.xlsx</div>
                </div>
                <div class="file-item" data-file-id="file-2-3">
                    <div class="file-icon doc">
                        <i class="fas fa-file-word"></i>
                    </div>
                    <div class="file-name">تقرير_الحضور.docx</div>
                </div>
            `;
            
            listHtml = `
                <tr data-file-id="file-2-1">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon xls">
                                <i class="fas fa-file-excel"></i>
                            </div>
                            <span>سجل_الحضور_ابريل.xlsx</span>
                        </div>
                    </td>
                    <td>جدول Excel</td>
                    <td>655 KB</td>
                    <td>19/04/2025</td>
                </tr>
                <tr data-file-id="file-2-2">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon xls">
                                <i class="fas fa-file-excel"></i>
                            </div>
                            <span>سجل_الحضور_مارس.xlsx</span>
                        </div>
                    </td>
                    <td>جدول Excel</td>
                    <td>578 KB</td>
                    <td>01/04/2025</td>
                </tr>
                <tr data-file-id="file-2-3">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon doc">
                                <i class="fas fa-file-word"></i>
                            </div>
                            <span>تقرير_الحضور.docx</span>
                        </div>
                    </td>
                    <td>مستند Word</td>
                    <td>325 KB</td>
                    <td>20/04/2025</td>
                </tr>
            `;
            
            itemCount = 3;
        }
        // إذا كان المجلد هو "حسابات" (رقم 3)، سنعرض ملفات مالية
        else if (folderId === 'folder-3' || realFolderId === '3') {
            filesHtml = `
                <div class="file-item" data-file-id="file-3-1">
                    <div class="file-icon xls">
                        <i class="fas fa-file-excel"></i>
                    </div>
                    <div class="file-name">ميزانية_2025.xlsx</div>
                </div>
                <div class="file-item" data-file-id="file-3-2">
                    <div class="file-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="file-name">تقرير_مالي_سنوي.pdf</div>
                </div>
                <div class="file-item" data-file-id="file-3-3">
                    <div class="file-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="file-name">فواتير_مارس.pdf</div>
                </div>
            `;
            
            listHtml = `
                <tr data-file-id="file-3-1">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon xls">
                                <i class="fas fa-file-excel"></i>
                            </div>
                            <span>ميزانية_2025.xlsx</span>
                        </div>
                    </td>
                    <td>جدول Excel</td>
                    <td>982 KB</td>
                    <td>15/04/2025</td>
                </tr>
                <tr data-file-id="file-3-2">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span>تقرير_مالي_سنوي.pdf</span>
                        </div>
                    </td>
                    <td>ملف PDF</td>
                    <td>1.5 MB</td>
                    <td>18/04/2025</td>
                </tr>
                <tr data-file-id="file-3-3">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span>فواتير_مارس.pdf</span>
                        </div>
                    </td>
                    <td>ملف PDF</td>
                    <td>750 KB</td>
                    <td>10/04/2025</td>
                </tr>
            `;
            
            itemCount = 3;
        }
        // إذا كان المجلد هو "محفوظات" (رقم 4)، سنعرض ملفات أرشيفية
        else if (folderId === 'folder-4' || realFolderId === '4') {
            filesHtml = `
                <div class="file-item" data-file-id="file-4-1">
                    <div class="file-icon zip">
                        <i class="fas fa-file-archive"></i>
                    </div>
                    <div class="file-name">أرشيف_2024.zip</div>
                </div>
                <div class="file-item" data-file-id="file-4-2">
                    <div class="file-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="file-name">سجلات_قديمة.pdf</div>
                </div>
            `;
            
            listHtml = `
                <tr data-file-id="file-4-1">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon zip">
                                <i class="fas fa-file-archive"></i>
                            </div>
                            <span>أرشيف_2024.zip</span>
                        </div>
                    </td>
                    <td>ملف مضغوط</td>
                    <td>15.7 MB</td>
                    <td>05/01/2025</td>
                </tr>
                <tr data-file-id="file-4-2">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span>سجلات_قديمة.pdf</span>
                        </div>
                    </td>
                    <td>ملف PDF</td>
                    <td>3.2 MB</td>
                    <td>12/02/2025</td>
                </tr>
            `;
            
            itemCount = 2;
        }
        // إذا كان المجلد هو "توكيلات" (رقم 5)، سنعرض ملفات توكيلات
        else if (folderId === 'folder-5' || realFolderId === '5') {
            filesHtml = `
                <div class="file-item" data-file-id="file-5-1">
                    <div class="file-icon doc">
                        <i class="fas fa-file-word"></i>
                    </div>
                    <div class="file-name">نموذج_توكيل_رسمي.docx</div>
                </div>
                <div class="file-item" data-file-id="file-5-2">
                    <div class="file-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="file-name">توكيل_محمد_احمد.pdf</div>
                </div>
                <div class="file-item" data-file-id="file-5-3">
                    <div class="file-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="file-name">توكيل_خالد_محمود.pdf</div>
                </div>
                <div class="file-item" data-file-id="file-5-4">
                    <div class="file-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="file-name">توكيل_عمر_سعيد.pdf</div>
                </div>
            `;
            
            listHtml = `
                <tr data-file-id="file-5-1">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon doc">
                                <i class="fas fa-file-word"></i>
                            </div>
                            <span>نموذج_توكيل_رسمي.docx</span>
                        </div>
                    </td>
                    <td>مستند Word</td>
                    <td>245 KB</td>
                    <td>20/04/2025</td>
                </tr>
                <tr data-file-id="file-5-2">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span>توكيل_محمد_احمد.pdf</span>
                        </div>
                    </td>
                    <td>ملف PDF</td>
                    <td>508 KB</td>
                    <td>19/04/2025</td>
                </tr>
                <tr data-file-id="file-5-3">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span>توكيل_خالد_محمود.pdf</span>
                        </div>
                    </td>
                    <td>ملف PDF</td>
                    <td>512 KB</td>
                    <td>18/04/2025</td>
                </tr>
                <tr data-file-id="file-5-4">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span>توكيل_عمر_سعيد.pdf</span>
                        </div>
                    </td>
                    <td>ملف PDF</td>
                    <td>495 KB</td>
                    <td>17/04/2025</td>
                </tr>
            `;
            
            itemCount = 4;
        }
        // إذا كان المجلد الجذر أو غير معروف، سنعرض المجلدات الرئيسية
        else {
            filesHtml = `
                <div class="folder-item" data-folder-id="folder-1">
                    <div class="folder-icon">
                        <i class="fas fa-folder"></i>
                    </div>
                    <div class="folder-name">رسوم (1)</div>
                </div>
                
                <div class="folder-item" data-folder-id="folder-2">
                    <div class="folder-icon">
                        <i class="fas fa-folder"></i>
                    </div>
                    <div class="folder-name">حضور (2)</div>
                </div>
                
                <div class="folder-item" data-folder-id="folder-3">
                    <div class="folder-icon">
                        <i class="fas fa-folder"></i>
                    </div>
                    <div class="folder-name">حسابات (3)</div>
                </div>
                
                <div class="folder-item" data-folder-id="folder-4">
                    <div class="folder-icon">
                        <i class="fas fa-folder"></i>
                    </div>
                    <div class="folder-name">محفوظات (4)</div>
                </div>
                
                <div class="folder-item" data-folder-id="folder-5">
                    <div class="folder-icon">
                        <i class="fas fa-folder"></i>
                    </div>
                    <div class="folder-name">توكيلات (5)</div>
                </div>
                
                <!-- ملفات (عينة) -->
                <div class="file-item" data-file-id="file-root-1">
                    <div class="file-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                    </div>
                    <div class="file-name">تقرير_مالي.pdf</div>
                </div>
                
                <div class="file-item" data-file-id="file-root-2">
                    <div class="file-icon doc">
                        <i class="fas fa-file-word"></i>
                    </div>
                    <div class="file-name">نموذج_توكيل.docx</div>
                </div>
                
                <div class="file-item" data-file-id="file-root-3">
                    <div class="file-icon xls">
                        <i class="fas fa-file-excel"></i>
                    </div>
                    <div class="file-name">جدول_الحضور.xlsx</div>
                </div>
            `;
            
            listHtml = `
                <!-- المجلدات -->
                <tr data-folder-id="folder-1">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon folder">
                                <i class="fas fa-folder"></i>
                            </div>
                            <span>رسوم (1)</span>
                        </div>
                    </td>
                    <td>مجلد ملفات</td>
                    <td>-</td>
                    <td>21/04/2025</td>
                </tr>
                
                <tr data-folder-id="folder-2">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon folder">
                                <i class="fas fa-folder"></i>
                            </div>
                            <span>حضور (2)</span>
                        </div>
                    </td>
                    <td>مجلد ملفات</td>
                    <td>-</td>
                    <td>21/04/2025</td>
                </tr>
                
                <tr data-folder-id="folder-3">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon folder">
                                <i class="fas fa-folder"></i>
                            </div>
                            <span>حسابات (3)</span>
                        </div>
                    </td>
                    <td>مجلد ملفات</td>
                    <td>-</td>
                    <td>21/04/2025</td>
                </tr>
                
                <tr data-folder-id="folder-4">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon folder">
                                <i class="fas fa-folder"></i>
                            </div>
                            <span>محفوظات (4)</span>
                        </div>
                    </td>
                    <td>مجلد ملفات</td>
                    <td>-</td>
                    <td>21/04/2025</td>
                </tr>
                
                <tr data-folder-id="folder-5">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon folder">
                                <i class="fas fa-folder"></i>
                            </div>
                            <span>توكيلات (5)</span>
                        </div>
                    </td>
                    <td>مجلد ملفات</td>
                    <td>-</td>
                    <td>21/04/2025</td>
                </tr>
                
                <!-- الملفات (عينة) -->
                <tr data-file-id="file-root-1">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <span>تقرير_مالي.pdf</span>
                        </div>
                    </td>
                    <td>ملف PDF</td>
                    <td>2.1 MB</td>
                    <td>20/04/2025</td>
                </tr>
                
                <tr data-file-id="file-root-2">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon doc">
                                <i class="fas fa-file-word"></i>
                            </div>
                            <span>نموذج_توكيل.docx</span>
                        </div>
                    </td>
                    <td>مستند Word</td>
                    <td>358 KB</td>
                    <td>19/04/2025</td>
                </tr>
                
                <tr data-file-id="file-root-3">
                    <td>
                        <div class="file-cell">
                            <div class="file-list-icon xls">
                                <i class="fas fa-file-excel"></i>
                            </div>
                            <span>جدول_الحضور.xlsx</span>
                        </div>
                    </td>
                    <td>جدول Excel</td>
                    <td>780 KB</td>
                    <td>18/04/2025</td>
                </tr>
            `;
        }
        
        // تحديث عرض الملفات
        $('#grid-view').html(filesHtml);
        
        // تحديث عرض القائمة
        $('#list-view tbody').html(listHtml);
        
        // تحديث عدد العناصر
        const itemCountText = itemCount > 0 ? `${itemCount} عنصر` : 'لا توجد عناصر';
        $('.item-count').text(itemCountText);
        
        // تحديث شريط الحالة
        $('.status-bar-item.item-count').text(itemCountText);
        
        // تفعيل التفاعل مع الملفات والمجلدات الجديدة
        initializeItemInteractions();
    }
    
    // ============= احداث النقر والتفاعل =============
    
    // تفعيل النقر على عناصر الوصول السريع
    $(document).on('click', '.quick-access-item', function(e) {
        e.preventDefault(); // منع السلوك الافتراضي للرابط
        const folderId = $(this).data('folder-id');
        if (folderId) {
            console.log(`تم النقر على عنصر الوصول السريع: ${folderId}`);
            
            // عرض محتويات المجلد
            showFolderContents(folderId);
            
            // تحديث العنوان في شريط العنوان
            const folderName = $(this).find('span').text();
            $('.address-text').html('<a href="#" class="text-decoration-none">الرئيسية</a>' + 
                '<span class="breadcrumb-separator">/</span>' + folderName);
            
            // تسجيل التنقل في التاريخ إذا كانت الوظيفة موجودة
            if (typeof recordNavigation === 'function') {
                recordNavigation('folder-' + folderId);
            }
            
            // تحديد المجلد في شجرة المجلدات إذا كانت متاحة
            try {
                if ($('#folder-tree').jstree(true)) {
                    $('#folder-tree').jstree('deselect_all', true);
                    $('#folder-tree').jstree('select_node', 'folder-' + folderId);
                }
            } catch (error) {
                console.log('خطأ في تحديد المجلد في شجرة المجلدات:', error);
            }
        }
    });
    
    // تفعيل النقر على المجلدات في عرض الشبكة (Grid View)
    $(document).on('click', '.folder-item', function(e) {
        const folderId = $(this).data('folder-id');
        if (folderId) {
            console.log(`تم النقر على مجلد في عرض الشبكة: ${folderId}`);
            
            // عرض محتويات المجلد
            showFolderContents(folderId);
            
            // تحديث العنوان في شريط العنوان
            const folderName = $(this).find('.folder-name').text();
            $('.address-text').html('<a href="#" class="text-decoration-none">الرئيسية</a>' + 
                '<span class="breadcrumb-separator">/</span>' + folderName);
            
            // تسجيل التنقل في التاريخ إذا كانت الوظيفة موجودة
            if (typeof recordNavigation === 'function') {
                recordNavigation(folderId);
            }
            
            // تحديد المجلد في شجرة المجلدات إذا كانت متاحة
            try {
                if ($('#folder-tree').jstree(true)) {
                    $('#folder-tree').jstree('deselect_all', true);
                    $('#folder-tree').jstree('select_node', folderId);
                }
            } catch (error) {
                console.log('خطأ في تحديد المجلد في شجرة المجلدات:', error);
            }
        }
    });
    
    // تفعيل النقر على المجلدات في عرض القائمة (List View)
    $(document).on('click', 'tr[data-folder-id]', function(e) {
        const folderId = $(this).data('folder-id');
        if (folderId) {
            console.log(`تم النقر على مجلد في عرض القائمة: ${folderId}`);
            
            // عرض محتويات المجلد
            showFolderContents(folderId);
            
            // تحديث العنوان في شريط العنوان
            const folderName = $(this).find('span').text();
            $('.address-text').html('<a href="#" class="text-decoration-none">الرئيسية</a>' + 
                '<span class="breadcrumb-separator">/</span>' + folderName);
            
            // تسجيل التنقل في التاريخ إذا كانت الوظيفة موجودة
            if (typeof recordNavigation === 'function') {
                recordNavigation(folderId);
            }
            
            // تحديد المجلد في شجرة المجلدات إذا كانت متاحة
            try {
                if ($('#folder-tree').jstree(true)) {
                    $('#folder-tree').jstree('deselect_all', true);
                    $('#folder-tree').jstree('select_node', folderId);
                }
            } catch (error) {
                console.log('خطأ في تحديد المجلد في شجرة المجلدات:', error);
            }
        }
    });
    
    // تفعيل النقر على الملفات (فتح نافذة معاينة)
    $(document).on('click', '.file-item, tr[data-file-id]', function(e) {
        const fileId = $(this).data('file-id');
        if (fileId) {
            console.log(`تم النقر على ملف: ${fileId}`);
            
            // تحديد نوع الملف وعرض رسالة مناسبة
            let fileName = '';
            let fileType = '';
            
            if ($(this).hasClass('file-item')) {
                fileName = $(this).find('.file-name').text();
                if ($(this).find('.file-icon').hasClass('pdf')) fileType = 'PDF';
                else if ($(this).find('.file-icon').hasClass('doc')) fileType = 'Word';
                else if ($(this).find('.file-icon').hasClass('xls')) fileType = 'Excel';
                else if ($(this).find('.file-icon').hasClass('zip')) fileType = 'ZIP';
                else fileType = 'مستند';
            } else {
                fileName = $(this).find('span').text();
                const cellText = $(this).find('td:nth-child(2)').text();
                if (cellText.includes('PDF')) fileType = 'PDF';
                else if (cellText.includes('Word')) fileType = 'Word';
                else if (cellText.includes('Excel')) fileType = 'Excel';
                else if (cellText.includes('مضغوط')) fileType = 'ZIP';
                else fileType = 'مستند';
            }
            
            // عرض نافذة المعاينة
            $('#previewModal .modal-title').text(fileName);
            $('#previewModalContent').html(`
                <div class="text-center py-5">
                    <div class="mb-4">
                        <i class="fas fa-file-${fileType.toLowerCase() === 'pdf' ? 'pdf' : 
                                                 fileType.toLowerCase() === 'word' ? 'word' :
                                                 fileType.toLowerCase() === 'excel' ? 'excel' : 
                                                 fileType.toLowerCase() === 'zip' ? 'archive' : 'alt'} fa-4x"></i>
                    </div>
                    <h5>معاينة ${fileName}</h5>
                    <p class="text-muted">جاري تحميل ملف ${fileType}...</p>
                    <div class="progress mb-3">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 75%"></div>
                    </div>
                    <p class="small">سيتم فتح الملف في التطبيق المناسب عند اكتمال التحميل.</p>
                </div>
            `);
            
            // إظهار النافذة
            const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
            previewModal.show();
        }
    });
    
    // ============= وظائف العرض =============
    
    // تفعيل أزرار تبديل العرض (شبكة/قائمة)
    $('#grid-view-btn').on('click', function() {
        $(this).addClass('active');
        $('#list-view-btn').removeClass('active');
        $('#grid-view').show();
        $('#list-view').hide();
    });
    
    $('#list-view-btn').on('click', function() {
        $(this).addClass('active');
        $('#grid-view-btn').removeClass('active');
        $('#list-view').show();
        $('#grid-view').hide();
    });
    
    // تفعيل زر البحث
    $('#content-search').on('keyup', function() {
        const searchText = $(this).val().toLowerCase();
        
        // بحث في عرض الشبكة
        $('.file-item, .folder-item').each(function() {
            const itemName = $(this).find('.file-name, .folder-name').text().toLowerCase();
            if (itemName.includes(searchText)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
        
        // بحث في عرض القائمة
        $('#list-view tbody tr').each(function() {
            const itemName = $(this).find('span').text().toLowerCase();
            if (itemName.includes(searchText)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    
    // تهيئة تفاعلات العناصر (مجلدات وملفات)
    window.initializeItemInteractions = function() {
        // تفعيل النقر المزدوج
        $('.folder-item').on('dblclick', function() {
            $(this).trigger('click');
        });
        
        $('.file-item').on('dblclick', function() {
            $(this).trigger('click');
        });
        
        // تفعيل تحديد العناصر
        $('.folder-item, .file-item').on('click', function(e) {
            if (!$(e.target).hasClass('folder-name') && !$(e.target).hasClass('file-name')) {
                $('.folder-item, .file-item').removeClass('selected');
                $(this).addClass('selected');
            }
        });
        
        // تفعيل النقر على الصفوف في القائمة
        $('#list-view tbody tr').on('click', function(e) {
            $('#list-view tbody tr').removeClass('selected');
            $(this).addClass('selected');
        });
    };
    
    // ============= تهيئة الصفحة =============
    
    // عرض المجلد الرئيسي عند تحميل الصفحة
    showFolderContents('folder-root');
    
    // تفعيل البحث في شجرة المجلدات
    $('#folder-search').on('keyup', function() {
        const searchText = $(this).val();
        if ($('#folder-tree').jstree(true)) {
            $('#folder-tree').jstree('search', searchText);
        }
    });
    
    // تفعيل زر التحديث
    $('#refresh-btn').on('click', function() {
        const currentFolder = $('.folder-item.selected').data('folder-id') || 'folder-root';
        showFolderContents(currentFolder);
    });
    
    // انتقال للمجلد الأب
    $('#up-btn').on('click', function() {
        // البحث عن المجلد الأب في شجرة المجلدات
        try {
            const currentNodeId = $('.folder-item.selected').data('folder-id') || 'folder-root';
            if (currentNodeId !== 'folder-root' && $('#folder-tree').jstree(true)) {
                const currentNode = $('#folder-tree').jstree('get_node', currentNodeId);
                const parentId = currentNode.parent;
                
                if (parentId && parentId !== '#') {
                    $('#folder-tree').jstree('select_node', parentId);
                } else {
                    showFolderContents('folder-root');
                    $('.address-text').html('<a href="#" class="text-decoration-none">الرئيسية</a>');
                }
            } else {
                showFolderContents('folder-root');
                $('.address-text').html('<a href="#" class="text-decoration-none">الرئيسية</a>');
            }
        } catch (error) {
            console.log('خطأ في الانتقال للمجلد الأب:', error);
            showFolderContents('folder-root');
            $('.address-text').html('<a href="#" class="text-decoration-none">الرئيسية</a>');
        }
    });
    
    // النقر على رابط الرئيسية
    $(document).on('click', '.address-text a', function(e) {
        e.preventDefault();
        showFolderContents('folder-root');
        $('.address-text').html('<a href="#" class="text-decoration-none">الرئيسية</a>');
    });
});