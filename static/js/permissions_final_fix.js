/**
 * حل نهائي لمشكلة عدم تزامن حالة الصلاحيات بين الواجهة وقاعدة البيانات
 * 
 * هذا الملف يقوم بحل المشكلات التالية:
 * 1. عدم تحديث واجهة المستخدم بعد الحفظ
 * 2. حفظ الصلاحيات بدون تحديث كامل للصفحة
 * 3. تحديث عدادات الصلاحيات بشكل صحيح
 */

// المتغيرات العامة
let formSubmitInProgress = false;
let savedPermissions = {};

// عند اكتمال تحميل المستند
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔄 تم تحميل نظام إدارة الصلاحيات المتقدم (الإصدار النهائي)");
    
    // استدعاء التهيئة الرئيسية
    initializeEnhancedPermissions();
    
    // محاولة تحميل الصلاحيات من العنصر المخفي
    loadSavedPermissionsFromHiddenElement();
});

/**
 * تهيئة نظام الصلاحيات المحسن
 */
function initializeEnhancedPermissions() {
    // إضافة معالج لنموذج الصلاحيات
    setupFormSubmitHandler();
    
    // تحديث واجهة المستخدم بناءً على البيانات الأولية
    setTimeout(updateUIFromPermissions, 500);
    
    // إضافة حقل مخفي للإشارة إلى استخدام الواجهة المحسنة
    addEnhancedUIField();
    
    // تهيئة زر الحفظ وتعطيل حفظ النموذج العادي
    setupSaveButton();
    
    // إضافة معالجات للصلاحيات
    addPermissionCardHandlers();
}

/**
 * إضافة حقل مخفي للإشارة إلى استخدام الواجهة المحسنة
 */
function addEnhancedUIField() {
    const form = document.querySelector('form#permissionsForm');
    if (form) {
        // التحقق من وجود الحقل بالفعل
        let enhancedUIField = document.getElementById('use_enhanced_ui');
        if (!enhancedUIField) {
            enhancedUIField = document.createElement('input');
            enhancedUIField.type = 'hidden';
            enhancedUIField.name = 'use_enhanced_ui';
            enhancedUIField.id = 'use_enhanced_ui';
            enhancedUIField.value = 'true';
            form.appendChild(enhancedUIField);
            console.log("✅ تمت إضافة حقل الواجهة المحسنة");
        }
    }
}

/**
 * إعداد معالج إرسال النموذج باستخدام AJAX
 */
function setupFormSubmitHandler() {
    const form = document.querySelector('form#permissionsForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        // منع السلوك الافتراضي للنموذج
        e.preventDefault();
        
        // التحقق من عدم وجود عملية إرسال جارية
        if (formSubmitInProgress) {
            console.log("⚠️ توجد عملية حفظ جارية بالفعل");
            return;
        }
        
        // تعيين علم الإرسال الجاري
        formSubmitInProgress = true;
        
        // إظهار مؤشر التحميل
        showLoadingIndicator();
        
        // جمع بيانات النموذج
        const formData = new FormData(form);
        
        // إرسال البيانات باستخدام Fetch API
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // إخفاء مؤشر التحميل
            hideLoadingIndicator();
            
            // التحقق من حالة الاستجابة
            if (data.status === 'success') {
                // حفظ الصلاحيات المستلمة
                if (data.permissions) {
                    savedPermissions = data.permissions;
                    console.log("✅ تم استلام الصلاحيات من الخادم:", savedPermissions);
                    
                    // تحديث واجهة المستخدم
                    updateUIFromPermissions();
                    
                    // عرض إشعار نجاح
                    showNotification('نجاح', data.message || 'تم حفظ الصلاحيات بنجاح');
                }
            } else {
                // عرض إشعار خطأ
                showNotification('خطأ', data.message || 'حدث خطأ أثناء حفظ الصلاحيات', 'error');
            }
            
            // إعادة تعيين علم الإرسال الجاري
            formSubmitInProgress = false;
        })
        .catch(error => {
            console.error("❌ خطأ في إرسال النموذج:", error);
            
            // إخفاء مؤشر التحميل
            hideLoadingIndicator();
            
            // عرض إشعار خطأ
            showNotification('خطأ', 'حدث خطأ أثناء الاتصال بالخادم', 'error');
            
            // إعادة تعيين علم الإرسال الجاري
            formSubmitInProgress = false;
        });
    });
}

/**
 * إعداد زر الحفظ المخصص
 */
function setupSaveButton() {
    const saveBtn = document.getElementById('savePermissionsBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // التحقق من جميع الصلاحيات المحددة وإضافة حقول مخفية لها
            addHiddenPermissionFields();
            
            // تقديم النموذج
            const form = document.querySelector('form#permissionsForm');
            if (form) {
                form.dispatchEvent(new Event('submit'));
            }
        });
    }
}

/**
 * إضافة معالجات لبطاقات الصلاحيات
 */
function addPermissionCardHandlers() {
    const permissionCards = document.querySelectorAll('.permission-card');
    
    permissionCards.forEach(card => {
        card.addEventListener('click', function() {
            // الحصول على معلومات الصلاحية
            const section = this.getAttribute('data-section');
            const permission = this.getAttribute('data-permission');
            
            // تبديل حالة التنشيط
            this.classList.toggle('active');
            
            // تحديث عداد القسم
            updateSectionCounter(section);
            
            console.log(`${this.classList.contains('active') ? '✅' : '❌'} ${section}_${permission}`);
        });
    });
}

/**
 * تحميل الصلاحيات المحفوظة من العنصر المخفي
 */
function loadSavedPermissionsFromHiddenElement() {
    const permissionsElement = document.getElementById('saved_permissions_json');
    if (permissionsElement) {
        try {
            const permissionsJSON = permissionsElement.value;
            if (permissionsJSON) {
                savedPermissions = JSON.parse(permissionsJSON);
                console.log("✅ تم تحميل الصلاحيات المحفوظة:", savedPermissions);
                
                // تحديث واجهة المستخدم
                updateUIFromPermissions();
            }
        } catch (error) {
            console.error("❌ خطأ في تحليل الصلاحيات المحفوظة:", error);
        }
    }
}

/**
 * تحديث واجهة المستخدم بناءً على الصلاحيات المحفوظة
 */
function updateUIFromPermissions() {
    console.log("🔄 جارٍ تحديث واجهة المستخدم بناءً على الصلاحيات المحفوظة");
    
    if (!savedPermissions || Object.keys(savedPermissions).length === 0) {
        console.log("⚠️ لا توجد صلاحيات محفوظة لتحديث الواجهة");
        return;
    }
    
    // تحديث جميع البطاقات
    const permissionCards = document.querySelectorAll('.permission-card');
    
    permissionCards.forEach(card => {
        const section = card.getAttribute('data-section');
        const permission = card.getAttribute('data-permission');
        
        // التحقق من وجود القسم والصلاحية في الصلاحيات المحفوظة
        const isActive = savedPermissions[section] && 
                        Array.isArray(savedPermissions[section]) && 
                        savedPermissions[section].includes(permission);
        
        // تحديث حالة البطاقة
        if (isActive) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });
    
    // تحديث جميع العدادات
    updateAllTabCounters();
}

/**
 * إضافة حقول مخفية للصلاحيات المحددة
 */
function addHiddenPermissionFields() {
    const form = document.querySelector('form#permissionsForm');
    if (!form) return;
    
    // إزالة الحقول المخفية السابقة
    const existingFields = form.querySelectorAll('input[type="hidden"][name^="dashboard_"], input[type="hidden"][name^="reservations_"]');
    existingFields.forEach(field => {
        field.remove();
    });
    
    // إضافة حقول مخفية للصلاحيات المحددة
    const activeCards = document.querySelectorAll('.permission-card.active');
    
    activeCards.forEach(card => {
        const section = card.getAttribute('data-section');
        const permission = card.getAttribute('data-permission');
        
        // إنشاء حقل جديد
        const hiddenField = document.createElement('input');
        hiddenField.type = 'hidden';
        hiddenField.name = `${section}_${permission}`;
        hiddenField.value = 'on';
        
        // إضافة الحقل إلى النموذج
        form.appendChild(hiddenField);
    });
    
    console.log(`✅ تمت إضافة ${activeCards.length} حقل مخفي للصلاحيات المحددة`);
}

/**
 * تحديث عداد الصلاحيات في قسم معين
 */
function updateSectionCounter(sectionId) {
    // الحصول على عدد البطاقات النشطة في هذا القسم
    const activeCards = document.querySelectorAll(`.permission-card[data-section="${sectionId}"].active`);
    const activeCount = activeCards.length;
    
    // تحديث العداد في التبويب
    const tabCounter = document.querySelector(`.nav-link[data-section="${sectionId}"] .badge`);
    if (tabCounter) {
        tabCounter.textContent = activeCount;
        
        // تحديث لون العداد
        if (activeCount > 0) {
            tabCounter.classList.remove('bg-secondary');
            tabCounter.classList.add('bg-primary');
        } else {
            tabCounter.classList.remove('bg-primary');
            tabCounter.classList.add('bg-secondary');
        }
    }
}

/**
 * تحديث جميع عدادات التبويبات
 */
function updateAllTabCounters() {
    // الحصول على جميع أقسام الصلاحيات
    const sections = document.querySelectorAll('.nav-link[data-section]');
    
    sections.forEach(section => {
        const sectionId = section.getAttribute('data-section');
        updateSectionCounter(sectionId);
    });
}

/**
 * إظهار مؤشر التحميل
 */
function showLoadingIndicator() {
    // التحقق من وجود مؤشر تحميل
    let loader = document.getElementById('permissionsLoader');
    
    // إنشاء مؤشر التحميل إذا لم يكن موجوداً
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'permissionsLoader';
        loader.className = 'permissions-loader';
        loader.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">جارٍ الحفظ...</span>
            </div>
            <p class="mt-2">جارٍ حفظ الصلاحيات...</p>
        `;
        
        // تطبيق الأنماط
        loader.style.position = 'fixed';
        loader.style.top = '0';
        loader.style.left = '0';
        loader.style.width = '100%';
        loader.style.height = '100%';
        loader.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        loader.style.display = 'flex';
        loader.style.flexDirection = 'column';
        loader.style.alignItems = 'center';
        loader.style.justifyContent = 'center';
        loader.style.zIndex = '9999';
        loader.style.color = 'white';
        
        // إضافة إلى الصفحة
        document.body.appendChild(loader);
    } else {
        // إظهار المؤشر الموجود
        loader.style.display = 'flex';
    }
}

/**
 * إخفاء مؤشر التحميل
 */
function hideLoadingIndicator() {
    const loader = document.getElementById('permissionsLoader');
    if (loader) {
        loader.style.display = 'none';
    }
}

/**
 * عرض إشعار للمستخدم
 */
function showNotification(title, message, type = 'success') {
    // التحقق من وجود عنصر الإشعارات
    let notifications = document.getElementById('permissionsNotifications');
    
    // إنشاء عنصر الإشعارات إذا لم يكن موجوداً
    if (!notifications) {
        notifications = document.createElement('div');
        notifications.id = 'permissionsNotifications';
        notifications.className = 'permissions-notifications';
        
        // تطبيق الأنماط
        notifications.style.position = 'fixed';
        notifications.style.top = '20px';
        notifications.style.right = '20px';
        notifications.style.zIndex = '9999';
        
        // إضافة إلى الصفحة
        document.body.appendChild(notifications);
    }
    
    // إنشاء الإشعار
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} shadow-sm`;
    notification.innerHTML = `
        <strong>${title}:</strong> ${message}
        <button type="button" class="btn-close" aria-label="إغلاق"></button>
    `;
    
    // تطبيق الأنماط
    notification.style.marginBottom = '10px';
    notification.style.minWidth = '300px';
    
    // إضافة إلى عنصر الإشعارات
    notifications.appendChild(notification);
    
    // إضافة معالج لزر الإغلاق
    const closeButton = notification.querySelector('.btn-close');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            notification.remove();
        });
    }
    
    // إزالة الإشعار تلقائياً بعد 5 ثوانٍ
    setTimeout(() => {
        notification.remove();
    }, 5000);
}