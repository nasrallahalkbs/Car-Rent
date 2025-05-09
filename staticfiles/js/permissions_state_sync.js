/**
 * إصلاح مشكلة عدم تحديث حالة الصلاحيات في الواجهة
 * 
 * هذا الملف يقوم بضمان تحديث حالة بطاقات الصلاحيات تلقائياً
 * بناءً على ما هو محفوظ في قاعدة البيانات عند تحميل الصفحة
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 تشغيل مزامنة حالة الصلاحيات v1.1');
    
    // الحصول على الصلاحيات المحفوظة في النظام على الفور
    loadSavedPermissions();
    
    // متغير للتحكم في تكرار التحديث
    let updateAttempts = 0;
    const maxUpdateAttempts = 3;
    
    // دالة التحديث المحسنة بعد الحفظ
    function updateUIAfterSave() {
        console.log(`⚡ تحديث واجهة الصلاحيات... محاولة ${updateAttempts + 1}/${maxUpdateAttempts}`);
        
        // تحديث البطاقات استناداً إلى قيمة عنصر saved-permissions
        const savedPermissionsElement = document.getElementById('saved-permissions');
        if (!savedPermissionsElement) {
            console.warn('⚠️ عنصر الصلاحيات المحفوظة غير موجود');
            return;
        }
        
        try {
            const savedPermissions = JSON.parse(savedPermissionsElement.value || '{}');
            console.log('📋 تحديث البطاقات باستخدام الصلاحيات:', savedPermissions);
            
            // تحديث كل بطاقة بناءً على البيانات المحفوظة
            document.querySelectorAll('.permission-card').forEach(card => {
                const section = card.closest('.permissions-section');
                if (!section) return;
                
                const sectionId = section.id.replace('section-', '');
                const permTitle = card.querySelector('.permission-title');
                if (!permTitle) return;
                
                const permName = permTitle.dataset.permName || 
                          permTitle.textContent.trim().toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
                
                const sectionPermissions = savedPermissions[sectionId] || [];
                
                // تطبيق الحالة المناسبة مع تسجيل تفصيلي
                if (sectionPermissions.includes(permName)) {
                    if (!card.classList.contains('active')) {
                        console.log(`➕ تفعيل صلاحية: ${sectionId}_${permName}`);
                        card.classList.add('active');
                    }
                } else {
                    if (card.classList.contains('active')) {
                        console.log(`➖ إلغاء صلاحية: ${sectionId}_${permName}`);
                        card.classList.remove('active');
                    }
                }
            });
            
            // تحديث جميع العدادات
            updateAllTabCounters();
            
            // للتأكد من عدم إعادة تحميل الصفحة
            if (window.location.search.includes('saved=true')) {
                window.history.replaceState({}, document.title, window.location.pathname);
            }
            
            return true;
        } catch (error) {
            console.error('❌ خطأ في تحديث واجهة المستخدم:', error);
            return false;
        }
    }
    
    // التحقق من وجود معلمة الحفظ في URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('saved') === 'true') {
        console.log('🔔 تم اكتشاف معلمة الحفظ في URL - جدولة تحديثات متكررة...');
        
        // جدولة عدة محاولات تحديث متتالية
        const updateInterval = setInterval(() => {
            const success = updateUIAfterSave();
            updateAttempts++;
            
            if (success || updateAttempts >= maxUpdateAttempts) {
                clearInterval(updateInterval);
                console.log(`✅ اكتمال تحديث واجهة الصلاحيات بعد ${updateAttempts} محاولات`);
                
                // تحديث نهائي
                if (!success) {
                    console.log('🔄 محاولة تحديث نهائية...');
                    loadSavedPermissions();
                }
                
                // إزالة معلمة URL
                window.history.replaceState({}, document.title, window.location.pathname);
            }
        }, 500);
    }
    
    // الاستماع لتغييرات البطاقات لتحديث العدادات فوراً
    document.querySelectorAll('.permission-card').forEach(card => {
        card.addEventListener('click', function() {
            // تأخير بسيط لضمان اكتمال التبديل بواسطة السكربت الآخر
            setTimeout(() => {
                const section = this.closest('.permissions-section');
                if (section) {
                    const sectionId = section.id.replace('section-', '');
                    updateSectionCounter(sectionId);
                }
            }, 50);
        });
    });
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