/**
 * إصلاح مشكلة عدم تحديث حالة الصلاحيات في الواجهة
 * 
 * هذا الملف يقوم بضمان تحديث حالة بطاقات الصلاحيات تلقائياً
 * بناءً على ما هو محفوظ في قاعدة البيانات عند تحميل الصفحة
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 تشغيل مزامنة حالة الصلاحيات v1.0');
    
    // الحصول على الصلاحيات المحفوظة في النظام
    loadSavedPermissions();
    
    // التأكد من التحديث بعد إعادة تحميل الصفحة (خاصة بعد الحفظ)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('saved') === 'true') {
        console.log('⚡ تم اكتشاف معلمة الحفظ في URL - جاري تحديث واجهة الصلاحيات...');
        
        // تأخير قصير للتأكد من أن كل شيء جاهز
        setTimeout(() => {
            loadSavedPermissions();
            
            // هذه خطوة إضافية لضمان أن البيانات محدثة
            document.querySelectorAll('.permission-card').forEach(card => {
                // التحقق من وجود بيانات الصلاحية
                const section = card.closest('.permissions-section');
                if (!section) return;
                
                const sectionId = section.id.replace('section-', '');
                const permTitle = card.querySelector('.permission-title');
                if (!permTitle) return;
                
                const permName = permTitle.dataset.permName || 
                          permTitle.textContent.trim().toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
                
                // فحص ما إذا كانت الصلاحية موجودة في قاعدة البيانات
                const savedPermissionsElement = document.getElementById('saved-permissions');
                if (!savedPermissionsElement) return;
                
                try {
                    const savedPermissions = JSON.parse(savedPermissionsElement.value || '{}');
                    const sectionPermissions = savedPermissions[sectionId] || [];
                    
                    // تطبيق الحالة المناسبة
                    if (sectionPermissions.includes(permName)) {
                        card.classList.add('active');
                    } else {
                        card.classList.remove('active');
                    }
                } catch (error) {
                    console.error('❌ خطأ في تحليل بيانات الصلاحيات:', error);
                }
            });
            
            // تحديث جميع العدادات
            updateAllTabCounters();
        }, 500);
    }
});

/**
 * تحميل الصلاحيات المحفوظة وتطبيقها على الواجهة
 */
function loadSavedPermissions() {
    // البيانات المحفوظة من النظام تأتي من Django في عنصر مخفي في HTML
    // يمكن أيضاً استدعاء API للحصول على البيانات المحدثة
    
    const savedPermissionsElement = document.getElementById('saved-permissions');
    if (!savedPermissionsElement) {
        console.warn('⚠️ عنصر الصلاحيات المحفوظة غير موجود');
        // إنشاء عنصر مخفي لحفظ الصلاحيات
        createSavedPermissionsElement();
        return;
    }
    
    try {
        // محاولة تحليل البيانات المحفوظة
        const savedPermissions = JSON.parse(savedPermissionsElement.value || '{}');
        console.log('📋 الصلاحيات المحفوظة:', savedPermissions);
        
        // تطبيق الصلاحيات على الواجهة
        applyPermissionsToUI(savedPermissions);
    } catch (error) {
        console.error('❌ خطأ في تحليل الصلاحيات المحفوظة:', error);
    }
}

/**
 * إنشاء عنصر مخفي لحفظ الصلاحيات من Django
 */
function createSavedPermissionsElement() {
    // الحصول على الصلاحيات من مصدر آخر إذا كان متاحاً
    // مثل سمات البيانات في النموذج
    const formElement = document.getElementById('permissions-form');
    
    if (formElement && formElement.dataset.permissions) {
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.id = 'saved-permissions';
        hiddenInput.value = formElement.dataset.permissions;
        
        formElement.appendChild(hiddenInput);
        console.log('✅ تم إنشاء عنصر الصلاحيات المحفوظة');
        
        // الآن بإمكاننا تحميل الصلاحيات
        loadSavedPermissions();
    } else {
        // استخراج الصلاحيات من البطاقات النشطة حالياً
        const currentPermissions = extractCurrentPermissions();
        console.log('🔍 الصلاحيات الحالية من الواجهة:', currentPermissions);
    }
}

/**
 * استخراج الصلاحيات الحالية من الواجهة
 */
function extractCurrentPermissions() {
    const currentPermissions = {};
    
    // فحص جميع أقسام الصلاحيات
    document.querySelectorAll('.permissions-section').forEach(section => {
        const sectionId = section.id.replace('section-', '');
        currentPermissions[sectionId] = [];
        
        // فحص جميع البطاقات النشطة في هذا القسم
        section.querySelectorAll('.permission-card.active').forEach(card => {
            const permTitle = card.querySelector('.permission-title');
            if (permTitle) {
                const permName = permTitle.dataset.permName || 
                              permTitle.textContent.trim().toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
                
                currentPermissions[sectionId].push(permName);
            }
        });
    });
    
    return currentPermissions;
}

/**
 * تطبيق الصلاحيات على واجهة المستخدم
 */
function applyPermissionsToUI(permissions) {
    console.log('🔄 تطبيق الصلاحيات على الواجهة...');
    
    // فحص جميع أقسام الصلاحيات
    document.querySelectorAll('.permissions-section').forEach(section => {
        const sectionId = section.id.replace('section-', '');
        const sectionPermissions = permissions[sectionId] || [];
        
        console.log(`⚡ مزامنة قسم ${sectionId}: ${sectionPermissions.length} صلاحية`);
        
        // فحص جميع البطاقات في هذا القسم
        section.querySelectorAll('.permission-card').forEach(card => {
            const permTitle = card.querySelector('.permission-title');
            if (permTitle) {
                // الحصول على اسم الصلاحية
                const permName = permTitle.dataset.permName || 
                              permTitle.textContent.trim().toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
                
                // تحديد ما إذا كانت الصلاحية مفعلة
                const isActive = sectionPermissions.includes(permName);
                
                // تطبيق الحالة على البطاقة
                if (isActive) {
                    card.classList.add('active');
                    console.log(`✅ تفعيل صلاحية: ${sectionId}_${permName}`);
                } else {
                    card.classList.remove('active');
                    console.log(`❌ إلغاء صلاحية: ${sectionId}_${permName}`);
                }
            }
        });
        
        // تحديث عداد الصلاحيات المفعلة في هذا القسم
        updateSectionCounter(sectionId);
    });
    
    // تحديث جميع عدادات التبويبات
    updateAllTabCounters();
}

/**
 * تحديث عداد الصلاحيات في قسم معين
 */
function updateSectionCounter(sectionId) {
    const section = document.getElementById(`section-${sectionId}`);
    if (!section) return;
    
    const totalCards = section.querySelectorAll('.permission-card').length;
    const activeCards = section.querySelectorAll('.permission-card.active').length;
    
    // تحديث العداد في القسم
    const sectionCounter = section.querySelector('.section-count');
    if (sectionCounter) {
        sectionCounter.textContent = `${activeCards} / ${totalCards}`;
    }
    
    // تحديث العداد في التبويب
    const tabCounter = document.querySelector(`.tab-item[data-section="${sectionId}"] .tab-count`);
    if (tabCounter) {
        tabCounter.textContent = activeCards;
        
        if (activeCards > 0) {
            tabCounter.classList.add('active');
        } else {
            tabCounter.classList.remove('active');
        }
    }
}

/**
 * تحديث جميع عدادات التبويبات
 */
function updateAllTabCounters() {
    document.querySelectorAll('.tab-item[data-section]').forEach(tab => {
        const sectionId = tab.dataset.section;
        const section = document.getElementById(`section-${sectionId}`);
        
        if (section) {
            const activeCards = section.querySelectorAll('.permission-card.active').length;
            
            // تحديث العداد
            const tabCounter = tab.querySelector('.tab-count');
            if (tabCounter) {
                tabCounter.textContent = activeCards;
                
                if (activeCards > 0) {
                    tabCounter.classList.add('active');
                } else {
                    tabCounter.classList.remove('active');
                }
            }
        }
    });
    
    console.log('✅ تم تحديث جميع عدادات التبويبات');
}