/**
 * معالج بيانات الصلاحيات
 * 
 * هذا الملف مسؤول عن تحديث حقل البيانات المخفي permissions_data
 * بناءً على الصلاحيات التي يتم تحديدها في واجهة المستخدم
 */

document.addEventListener('DOMContentLoaded', function() {
    // العثور على الحقل المخفي لتخزين بيانات الصلاحيات
    const permissionsDataField = document.getElementById('permissions_data');
    
    // التحقق من وجود الحقل المخفي
    if (!permissionsDataField) {
        console.error('لم يتم العثور على حقل بيانات الصلاحيات permissions_data!');
        return;
    }
    
    console.log('⚡ تم تحميل معالج بيانات الصلاحيات - الإصدار المحسن');
    
    // تهيئة كائن البيانات
    let permissionsData = {};
    
    // محاولة تحميل البيانات الموجودة
    try {
        permissionsData = JSON.parse(permissionsDataField.value || '{}');
        console.log('✅ تم تحميل البيانات الموجودة:', permissionsData);
    } catch (error) {
        console.error('❌ خطأ في تحليل بيانات الصلاحيات:', error);
        permissionsData = {};
    }
    
    // العثور على حقل الصلاحيات المحفوظة (للتهيئة الأولية)
    const savedPermissionsJson = document.getElementById('saved_permissions_json');
    if (savedPermissionsJson) {
        try {
            const savedData = JSON.parse(savedPermissionsJson.value || '{}');
            console.log('✅ تم تحميل البيانات المحفوظة سابقًا:', savedData);
            
            // نسخ البيانات المحفوظة إلى المتغير العام
            if (typeof window.savedPermissions !== 'undefined') {
                window.savedPermissions = savedData;
                console.log('✅ تم تحديث المتغير العام savedPermissions');
            }
            
            // استخدام البيانات المحفوظة لوضع الحالة الأولية إذا لم تكن البيانات موجودة
            if (Object.keys(permissionsData).length === 0) {
                permissionsData = savedData;
                console.log('✅ تم استخدام البيانات المحفوظة لتهيئة الحالة الأولية');
            }
        } catch (error) {
            console.error('❌ خطأ في تحليل البيانات المحفوظة:', error);
        }
    }
    
    /**
     * تحديث البيانات بناءً على حالة الصلاحيات في الواجهة
     */
    function updatePermissionsData() {
        // إعادة تهيئة كائن البيانات
        permissionsData = {};
        
        // الحصول على جميع أقسام الصلاحيات
        const sectionElements = document.querySelectorAll('.permissions-section');
        console.log(`تم العثور على ${sectionElements.length} قسم من أقسام الصلاحيات`);
        
        // معالجة كل قسم
        sectionElements.forEach(section => {
            // استخراج معرف القسم
            const sectionId = section.id.replace('section-', '');
            console.log(`معالجة القسم: ${sectionId}`);
            
            // تهيئة مصفوفة الصلاحيات لهذا القسم
            permissionsData[sectionId] = [];
            
            // العثور على جميع بطاقات الصلاحيات النشطة في هذا القسم
            const activeCards = section.querySelectorAll('.permission-card.active');
            console.log(`تم العثور على ${activeCards.length} صلاحية نشطة في قسم ${sectionId}`);
            
            // استخراج اسم الصلاحية من كل بطاقة نشطة
            activeCards.forEach(card => {
                let permissionName = null;
                
                // محاولة الحصول على اسم الصلاحية من سمة data-permission-name أولاً
                if (card.hasAttribute('data-permission-name')) {
                    permissionName = card.getAttribute('data-permission-name');
                }
                
                // ثم محاولة الحصول على اسم الصلاحية من سمة data-perm-name في عنوان الصلاحية
                if (!permissionName) {
                    const title = card.querySelector('.permission-title');
                    if (title && title.hasAttribute('data-perm-name')) {
                        permissionName = title.getAttribute('data-perm-name');
                    }
                }
                
                // إذا لم يتم العثور على اسم الصلاحية، استخدم النص
                if (!permissionName) {
                    const title = card.querySelector('.permission-title');
                    if (title) {
                        const titleText = title.textContent.trim();
                        
                        // تحويل النص العربي إلى مفتاح إنجليزي استنادًا إلى بعض القواعد البسيطة
                        if (titleText.includes('عرض') || titleText.includes('الاطلاع')) {
                            permissionName = 'view_' + sectionId;
                        } else if (titleText.includes('إضافة') || titleText.includes('إنشاء')) {
                            permissionName = 'create_' + sectionId.replace(/s$/, '');
                        } else if (titleText.includes('تعديل')) {
                            permissionName = 'edit_' + sectionId.replace(/s$/, '');
                        } else if (titleText.includes('حذف')) {
                            permissionName = 'delete_' + sectionId.replace(/s$/, '');
                        } else if (titleText.includes('إدارة')) {
                            permissionName = 'manage_' + sectionId;
                        } else {
                            // استخراج المفتاح من النص مع إزالة الأحرف غير اللاتينية والمسافات
                            permissionName = titleText.toLowerCase()
                                .replace(/[^\w\s]/gi, '')
                                .replace(/\s+/g, '_');
                        }
                    }
                }
                
                // إضافة اسم الصلاحية إلى مصفوفة الصلاحيات لهذا القسم
                if (permissionName && !permissionsData[sectionId].includes(permissionName)) {
                    permissionsData[sectionId].push(permissionName);
                    console.log(`إضافة الصلاحية "${permissionName}" إلى قسم "${sectionId}"`);
                }
            });
        });
        
        // تحديث قيمة الحقل المخفي
        permissionsDataField.value = JSON.stringify(permissionsData);
        console.log('تم تحديث بيانات الصلاحيات:', permissionsData);
    }
    
    // إضافة مستمعي الأحداث إلى بطاقات الصلاحيات
    const permissionCards = document.querySelectorAll('.permission-card');
    console.log(`تم العثور على ${permissionCards.length} بطاقة صلاحيات في الصفحة`);
    
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
    const form = document.querySelector('form');
    if (form) {
        console.log('تم العثور على النموذج، إضافة مستمع الأحداث للإرسال');
        
        form.addEventListener('submit', function(e) {
            // تحديث البيانات قبل إرسال النموذج
            console.log('النموذج يتم إرساله، تحديث بيانات الصلاحيات...');
            updatePermissionsData();
        });
    } else {
        console.warn('لم يتم العثور على نموذج في الصفحة!');
    }
    
    // إضافة مستمعي الأحداث لأزرار تحديد/إلغاء تحديد الكل
    const selectAllBtn = document.getElementById('select-all-permissions');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            console.log('تم النقر على زر تحديد الكل');
            
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
            console.log('تم النقر على زر إلغاء تحديد الكل');
            
            permissionCards.forEach(card => {
                card.classList.remove('active');
            });
            
            // تحديث البيانات
            updatePermissionsData();
        });
    }
    
    // تهيئة قيم الصلاحيات بناءً على البيانات المحفوظة
    function initializePermissionCards() {
        console.log('تهيئة بطاقات الصلاحيات بناءً على البيانات المحفوظة');
        
        // إزالة الفئة "active" من جميع البطاقات أولاً
        permissionCards.forEach(card => {
            card.classList.remove('active');
        });
        
        // تحديد البطاقات النشطة بناءً على البيانات المحفوظة
        Object.entries(permissionsData).forEach(([sectionId, permissions]) => {
            const section = document.getElementById(`section-${sectionId}`);
            if (!section) {
                console.warn(`لم يتم العثور على القسم: ${sectionId}`);
                return;
            }
            
            permissions.forEach(permission => {
                // البحث عن البطاقات المناسبة استنادًا إلى سمات البيانات أو النص
                const cards = section.querySelectorAll('.permission-card');
                
                cards.forEach(card => {
                    const cardText = card.textContent.trim().toLowerCase();
                    const title = card.querySelector('.permission-title');
                    
                    let isMatch = false;
                    
                    // التحقق من سمة البيانات أولاً
                    if (card.hasAttribute('data-permission-name') && card.getAttribute('data-permission-name') === permission) {
                        isMatch = true;
                    } else if (title && title.hasAttribute('data-perm-name') && title.getAttribute('data-perm-name') === permission) {
                        isMatch = true;
                    } else {
                        // التحقق من النص بالتطابق الجزئي
                        if (permission.includes('view') && (cardText.includes('عرض') || cardText.includes('اطلاع'))) {
                            isMatch = true;
                        } else if (permission.includes('create') && (cardText.includes('إضافة') || cardText.includes('إنشاء'))) {
                            isMatch = true;
                        } else if (permission.includes('edit') && cardText.includes('تعديل')) {
                            isMatch = true;
                        } else if (permission.includes('delete') && cardText.includes('حذف')) {
                            isMatch = true;
                        } else if (permission.includes('manage') && cardText.includes('إدارة')) {
                            isMatch = true;
                        }
                    }
                    
                    if (isMatch) {
                        card.classList.add('active');
                        console.log(`تم تنشيط بطاقة الصلاحية: ${title ? title.textContent : card.textContent}`);
                    }
                });
            });
        });
        
        // تحديث تعداد الصلاحيات في كل قسم
        updatePermissionCounts();
    }
    
    // تحديث تعداد الصلاحيات في علامات التبويب
    function updatePermissionCounts() {
        const tabs = document.querySelectorAll('.tab-item');
        
        tabs.forEach(tab => {
            if (!tab.hasAttribute('data-section')) return;
            
            const sectionName = tab.getAttribute('data-section');
            const section = document.getElementById(`section-${sectionName}`);
            
            if (section) {
                const count = section.querySelectorAll('.permission-card.active').length;
                const countElement = tab.querySelector('.action-count');
                
                if (countElement) {
                    countElement.textContent = count;
                }
            }
        });
    }
    
    // تحديث البيانات عند تحميل الصفحة
    console.log('بدء تهيئة الصلاحيات وتحديث البيانات');
    initializePermissionCards();
    updatePermissionsData();
    
    console.log('تم الانتهاء من تحميل وتهيئة معالج بيانات الصلاحيات');
});