/**
 * معالج الصلاحيات الديناميكي
 * هذا الملف يقوم بتحديث حقل الإدخال المخفي permissions_data
 * بناءً على الصلاحيات التي يحددها المستخدم في واجهة المستخدم
 */

document.addEventListener('DOMContentLoaded', function() {
    // الحصول على العناصر المطلوبة
    const permissionsDataField = document.getElementById('permissions_data');
    const permissionCards = document.querySelectorAll('.permission-card');
    const permissionCheckboxes = document.querySelectorAll('.permission-checkbox');
    
    // تهيئة كائن الصلاحيات المحددة
    let selectedPermissions = {};
    
    // تحميل الصلاحيات المحددة مسبقًا
    try {
        selectedPermissions = JSON.parse(permissionsDataField.value || '{}');
    } catch (error) {
        console.error('خطأ في تحليل بيانات الصلاحيات:', error);
        selectedPermissions = {};
    }
    
    // دالة لتحديث حقل البيانات المخفي
    function updatePermissionsData() {
        // إعادة بناء كائن الصلاحيات المحددة
        selectedPermissions = {};
        
        // فحص جميع البطاقات النشطة والحصول على القسم واسم الصلاحية
        permissionCards.forEach(card => {
            const isActive = card.classList.contains('active');
            const sectionElement = card.closest('.permissions-section');
            const section = sectionElement ? sectionElement.id.replace('section-', '') : '';
            const permElement = card.querySelector('.permission-title');
            const permName = permElement ? permElement.getAttribute('data-perm-name') : '';
            
            // إذا كانت البطاقة نشطة، أضف الصلاحية إلى الكائن
            if (isActive && section && permName) {
                if (!selectedPermissions[section]) {
                    selectedPermissions[section] = [];
                }
                
                // تجنب التكرار
                if (!selectedPermissions[section].includes(permName)) {
                    selectedPermissions[section].push(permName);
                }
            }
        });
        
        // تحديث حقل البيانات المخفي
        permissionsDataField.value = JSON.stringify(selectedPermissions);
        console.log('تم تحديث بيانات الصلاحيات:', selectedPermissions);
    }

    // إضافة مستمعي الأحداث لبطاقات الصلاحيات
    permissionCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // تجاهل النقر إذا كان على عنصر تفاعلي داخل البطاقة
            if (e.target.closest('a, button') || e.target.tagName === 'A' || e.target.tagName === 'BUTTON') {
                return;
            }
            
            // تبديل حالة البطاقة
            this.classList.toggle('active');
            
            // تحديث حالة صندوق الاختيار
            const checkbox = this.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.checked = this.classList.contains('active');
            }
            
            // تحديث البيانات المخفية
            updatePermissionsData();
        });
    });

    // إضافة مستمع للتغييرات في صناديق الاختيار
    permissionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // تحديث حالة البطاقة
            const card = this.closest('.permission-card');
            if (card) {
                if (this.checked) {
                    card.classList.add('active');
                } else {
                    card.classList.remove('active');
                }
            }
            
            // تحديث البيانات المخفية
            updatePermissionsData();
        });
    });

    // إعداد زر تحديد الكل
    const selectAllBtn = document.getElementById('select-all-permissions');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            // تحديد جميع البطاقات
            permissionCards.forEach(card => {
                card.classList.add('active');
                const checkbox = card.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
            
            // تحديث البيانات المخفية
            updatePermissionsData();
        });
    }

    // إعداد زر إلغاء تحديد الكل
    const deselectAllBtn = document.getElementById('deselect-all-permissions');
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function() {
            // إلغاء تحديد جميع البطاقات
            permissionCards.forEach(card => {
                card.classList.remove('active');
                const checkbox = card.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = false;
                }
            });
            
            // تحديث البيانات المخفية
            updatePermissionsData();
        });
    }

    // تحديث حقل البيانات المخفي عند تحميل الصفحة
    updatePermissionsData();
});