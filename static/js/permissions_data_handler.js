/**
 * معالج بيانات الصلاحيات
 * 
 * هذا الملف مسؤول عن تحديث حقل البيانات المخفي permissions_data
 * بناءً على الصلاحيات التي يتم تحديدها في واجهة المستخدم
 */

document.addEventListener('DOMContentLoaded', function() {
    // العثور على الحقل المخفي لتخزين بيانات الصلاحيات
    const permissionsDataField = document.getElementById('permissions_data');
    
    // تهيئة كائن البيانات
    let permissionsData = {};
    
    // محاولة تحميل البيانات الموجودة
    try {
        permissionsData = JSON.parse(permissionsDataField.value || '{}');
    } catch (error) {
        console.error('خطأ في تحليل بيانات الصلاحيات:', error);
        permissionsData = {};
    }
    
    /**
     * تحديث البيانات بناءً على حالة الصلاحيات في الواجهة
     */
    function updatePermissionsData() {
        // إعادة تهيئة كائن البيانات
        permissionsData = {};
        
        // الحصول على جميع أقسام الصلاحيات
        const sectionElements = document.querySelectorAll('.permissions-section');
        
        // معالجة كل قسم
        sectionElements.forEach(section => {
            // استخراج معرف القسم
            const sectionId = section.id.replace('section-', '');
            
            // تهيئة مصفوفة الصلاحيات لهذا القسم
            permissionsData[sectionId] = [];
            
            // العثور على جميع بطاقات الصلاحيات النشطة في هذا القسم
            const activeCards = section.querySelectorAll('.permission-card.active');
            
            // استخراج اسم الصلاحية من كل بطاقة نشطة
            activeCards.forEach(card => {
                const title = card.querySelector('.permission-title');
                
                // استخراج اسم الصلاحية من سمة البيانات
                // إذا كانت متوفرة، وإلا استخدم النص
                let permissionName = title.getAttribute('data-perm-name');
                
                // إذا لم يكن هناك سمة بيانات، حاول استخراج الاسم من النص
                if (!permissionName) {
                    // تحويل النص إلى مفتاح (مثلًا: "عرض لوحة التحكم" -> "view_dashboard")
                    const titleText = title.textContent.trim();
                    
                    // تحويل النص العربي إلى مفتاح إنجليزي استنادًا إلى بعض القواعد البسيطة
                    if (titleText.includes('عرض') || titleText.includes('الاطلاع')) {
                        permissionName = 'view_' + sectionId;
                    } else if (titleText.includes('إضافة') || titleText.includes('إنشاء')) {
                        permissionName = 'create_' + sectionId.replace('s', '');
                    } else if (titleText.includes('تعديل')) {
                        permissionName = 'edit_' + sectionId.replace('s', '');
                    } else if (titleText.includes('حذف')) {
                        permissionName = 'delete_' + sectionId.replace('s', '');
                    } else if (titleText.includes('إدارة')) {
                        permissionName = 'manage_' + sectionId;
                    } else {
                        // تكوين مفتاح افتراضي
                        permissionName = titleText.toLowerCase()
                            .replace(/\s+/g, '_')
                            .replace(/[^\w\s]/gi, '');
                    }
                }
                
                // إضافة اسم الصلاحية إلى مصفوفة الصلاحيات لهذا القسم
                if (permissionName && !permissionsData[sectionId].includes(permissionName)) {
                    permissionsData[sectionId].push(permissionName);
                }
            });
        });
        
        // تحديث قيمة الحقل المخفي
        permissionsDataField.value = JSON.stringify(permissionsData);
        console.log('تم تحديث بيانات الصلاحيات:', permissionsData);
    }
    
    // إضافة مستمعي الأحداث إلى بطاقات الصلاحيات
    const permissionCards = document.querySelectorAll('.permission-card');
    permissionCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // تجاهل النقر إذا كان على عنصر تفاعلي داخل البطاقة
            if (e.target.closest('a, button') || e.target.tagName === 'A' || e.target.tagName === 'BUTTON') {
                return;
            }
            
            // تبديل حالة البطاقة
            this.classList.toggle('active');
            
            // تحديث بيانات الصلاحيات
            updatePermissionsData();
        });
    });
    
    // إضافة مستمع للنموذج قبل الإرسال
    const form = document.getElementById('permissions-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // تحديث البيانات قبل إرسال النموذج
            updatePermissionsData();
        });
    }
    
    // إضافة مستمعي الأحداث لأزرار تحديد/إلغاء تحديد الكل
    const selectAllBtn = document.getElementById('select-all-permissions');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            permissionCards.forEach(card => {
                card.classList.add('active');
            });
            
            // تحديث البيانات
            updatePermissionsData();
        });
    }
    
    const deselectAllBtn = document.getElementById('deselect-all-permissions');
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function() {
            permissionCards.forEach(card => {
                card.classList.remove('active');
            });
            
            // تحديث البيانات
            updatePermissionsData();
        });
    }
    
    // تحديث البيانات عند تحميل الصفحة
    updatePermissionsData();
});