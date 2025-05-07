/**
 * سكريبت محسن بالكامل لصفحة الصلاحيات المتقدمة
 * بُني من الصفر لضمان عمل وظائف التبويبات وبطاقات الصلاحيات بشكل صحيح
 */

$(document).ready(function() {
    // تهيئة نظام التبويبات
    initializeTabs();
    
    // تفعيل بطاقات الصلاحيات
    initializePermissionCards();
    
    // تفعيل أزرار تحديد الكل
    initializeSelectAllButtons();
    
    // تفعيل زر حفظ التغييرات
    initializeSaveButton();
    
    // الأزرار العامة
    bindUtilityButtons();
});

/**
 * تهيئة نظام التبويبات
 */
function initializeTabs() {
    // عند النقر على تبويب
    $('.tab-item').on('click', function(e) {
        // منع السلوك الافتراضي
        e.preventDefault();
        e.stopPropagation();
        
        // تجاهل زر فتح الكل لأنه له معالج منفصل
        if ($(this).hasClass('utility')) {
            return false;
        }
        
        // الحصول على القسم المستهدف
        const targetSection = $(this).data('section');
        
        // تحديث حالة التبويبات
        $('.tab-item').removeClass('active');
        $(this).addClass('active');
        
        // عرض القسم المطلوب وإخفاء البقية
        $('.permissions-section').removeClass('active');
        $(`#section-${targetSection}`).addClass('active');
        
        // حفظ التبويب المحدد في التخزين المحلي
        localStorage.setItem('activePermissionsTab', targetSection);
        
        return false;
    });
    
    // تحميل التبويب المختار سابقًا أو التبويب الأول
    const savedTab = localStorage.getItem('activePermissionsTab');
    if (savedTab && $(`.tab-item[data-section="${savedTab}"]`).length) {
        $(`.tab-item[data-section="${savedTab}"]`).click();
    } else {
        // تفعيل التبويب الأول
        $('.tab-item:not(.utility)').first().click();
    }
}

/**
 * تهيئة بطاقات الصلاحيات
 */
function initializePermissionCards() {
    // تتبع التغييرات
    let changesCount = 0;
    
    // عند النقر على بطاقة صلاحية
    $('.permission-card').on('click', function() {
        // منع التفاعل مع بطاقات الصلاحيات للمسؤول الأعلى
        if ($('#is-superadmin').val() === 'true') {
            showNotification('تنبيه', 'لا يمكن تعديل صلاحيات المسؤول الأعلى', 'warning');
            return;
        }
        
        // تبديل حالة البطاقة
        $(this).toggleClass('active');
        
        // تحديث عدد الصلاحيات المفعلة
        updatePermissionCounts();
        
        // زيادة عداد التغييرات
        changesCount++;
    });
    
    // إضافة زر لحفظ جميع التغييرات في الصفحة
    if ($('#save-all-permissions-btn').length === 0) {
        const saveButton = $('<button>').attr({
            id: 'save-all-permissions-btn',
            type: 'button',
            class: 'action-btn primary save-all-btn'
        }).css({
            position: 'fixed',
            bottom: '20px',
            left: '20px',
            padding: '10px 15px',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
        }).html('<i class="fas fa-save"></i> <span>حفظ جميع الصلاحيات</span>');
        
        // إضافة مؤشر التغييرات
        const changesIndicator = $('<span>').attr({
            id: 'changes-counter',
            class: 'badge badge-light'
        }).css({
            display: 'inline-block',
            minWidth: '20px',
            height: '20px',
            lineHeight: '20px',
            background: '#f8f9fa',
            color: '#212529',
            borderRadius: '50%',
            textAlign: 'center',
            marginRight: '5px',
            fontSize: '12px'
        }).text('0');
        
        saveButton.prepend(changesIndicator);
        
        // إخفاء الزر في البداية حتى يتم إجراء تغييرات
        saveButton.hide();
        
        // إضافة حدث النقر على زر الحفظ
        saveButton.on('click', function() {
            saveAllPermissions();
            changesCount = 0;
            $('#changes-counter').text('0');
            $(this).hide();
        });
        
        // إضافة الزر للصفحة
        $('body').append(saveButton);
    }
    
    // تحديث عداد التغييرات كل ثانية
    setInterval(() => {
        if (changesCount > 0) {
            $('#save-all-permissions-btn').show();
            $('#changes-counter').text(changesCount);
        }
    }, 1000);
    
    // تحديث عداد الصلاحيات المفعلة عند التحميل
    updatePermissionCounts();
}

/**
 * حفظ جميع الصلاحيات
 */
function saveAllPermissions() {
    // إضافة حقول مخفية للصلاحيات المختارة
    addHiddenPermissionFields();
    
    // عرض مؤشر جاري الحفظ
    const saveNotificationId = 'save-notification';
    if ($('#' + saveNotificationId).length === 0) {
        const notification = $('<div>').attr({
            id: saveNotificationId,
            class: 'save-indicator'
        }).css({
            position: 'fixed',
            bottom: '70px',
            left: '20px',
            background: '#4caf50',
            color: 'white',
            padding: '10px 15px',
            borderRadius: '4px',
            boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            zIndex: 9999
        }).html('<i class="fas fa-spinner fa-spin"></i> <span>جارِ حفظ التغييرات...</span>');
        
        $('body').append(notification);
        
        // إرسال النموذج
        $('#permissions-form').submit();
        
        // بعد إتمام الإرسال
        setTimeout(() => {
            $('#' + saveNotificationId).html('<i class="fas fa-check-circle"></i> <span>تم حفظ التغييرات</span>');
            setTimeout(() => {
                $('#' + saveNotificationId).fadeOut(300, function() {
                    $(this).remove();
                });
            }, 1500);
        }, 1000);
    }
}

/**
 * تهيئة أزرار تحديد الكل
 */
function initializeSelectAllButtons() {
    $('.select-all').on('click', function(e) {
        // منع أي سلوك افتراضي للزر
        e.preventDefault();
        e.stopPropagation();
        
        // منع التفاعل مع الصلاحيات للمسؤول الأعلى
        if ($('#is-superadmin').val() === 'true') {
            showNotification('تنبيه', 'لا يمكن تعديل صلاحيات المسؤول الأعلى', 'warning');
            return;
        }
        
        // الحصول على القسم المستهدف
        const sectionId = $(this).data('section');
        const section = $(`#section-${sectionId}`);
        const cards = section.find('.permission-card');
        
        // تحديد ما إذا كانت جميع البطاقات مفعلة
        const allSelected = cards.length === cards.filter('.active').length;
        
        if (allSelected) {
            // إذا كان الكل محدد، قم بإلغاء التحديد
            cards.removeClass('active');
        } else {
            // وإلا قم بتحديد الكل
            cards.addClass('active');
        }
        
        // تحديث العداد
        updatePermissionCounts();
        
        // زيادة عداد التغييرات
        const currentCount = parseInt($('#changes-counter').text() || '0');
        const newCount = currentCount + cards.length;
        $('#changes-counter').text(newCount);
        $('#save-all-permissions-btn').show();
        
        // تأكيد للمستخدم
        showNotification(
            'تم',
            allSelected ? 'تم إلغاء تحديد جميع الصلاحيات' : 'تم تحديد جميع الصلاحيات',
            'success'
        );
        
        return false;
    });
}

/**
 * تهيئة زر حفظ التغييرات - متوقف
 */
function initializeSaveButton() {
    // هذه الوظيفة متوقفة ولم تعد تستخدم
    // يتم استخدام زر حفظ جميع الصلاحيات بدلاً منها
}

/**
 * إضافة حقول مخفية للصلاحيات المختارة
 */
function addHiddenPermissionFields() {
    // حذف الحقول المخفية السابقة
    $('#permissions-form input[type="hidden"][name^="checkbox_"]').remove();
    $('#permissions-form input[type="hidden"][name^="perm_"]').remove();
    $('#permissions-form input[type="hidden"][name$="_view"]').remove();
    $('#permissions-form input[type="hidden"][name$="_edit"]').remove();
    $('#permissions-form input[type="hidden"][name$="_create"]').remove();
    $('#permissions-form input[type="hidden"][name$="_delete"]').remove();
    
    // إضافة حقول مخفية لجميع الصلاحيات المفعلة
    $('.permissions-section').each(function() {
        const sectionId = $(this).attr('id').replace('section-', '');
        
        // فحص جميع البطاقات النشطة في هذا القسم
        $(this).find('.permission-card').each(function() {
            const permTitle = $(this).find('.permission-title').text().trim();
            const permName = $(this).find('.permission-title').data('perm-name') || 
                            permTitle.toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
            
            // إذا كانت البطاقة نشطة
            if ($(this).hasClass('active')) {
                // إنشاء حقل مخفي للصلاحية
                // الطريقة 1: باستخدام معرف مباشر كما في request.POST.get(f"{section}_{perm}")
                const directField = $('<input>').attr({
                    type: 'hidden',
                    name: sectionId + '_' + permName,
                    value: 'on'
                });
                $('#permissions-form').append(directField);
                
                // الطريقة 2: باستخدام النمط القديم section_action_section
                let permType = 'view'; // الافتراضي للصلاحيات
                const permLevel = $(this).find('.permission-level').text().trim();
                
                // تحديد نوع الصلاحية بناءً على النص أو مستوى الصلاحية
                if (permLevel === 'R' || permTitle.indexOf('عرض') !== -1 || permTitle.indexOf('الاطلاع') !== -1) {
                    permType = 'view';
                } else if (permLevel === 'W') {
                    if (permTitle.indexOf('تعديل') !== -1) {
                        permType = 'edit';
                    } else if (permTitle.indexOf('إضافة') !== -1 || permTitle.indexOf('إنشاء') !== -1) {
                        permType = 'create';
                    } else {
                        permType = 'edit'; // الافتراضي للكتابة
                    }
                } else if (permLevel === 'D' || permTitle.indexOf('حذف') !== -1) {
                    permType = 'delete';
                }
                
                // إضافة حقل بالنمط القديم
                const legacyField = $('<input>').attr({
                    type: 'hidden',
                    name: sectionId + '_' + permType + '_' + sectionId,
                    value: 'on'
                });
                $('#permissions-form').append(legacyField);
                
                // إضافة اسم الصلاحية المباشر
                const permField = $('<input>').attr({
                    type: 'hidden',
                    name: permName,
                    value: 'on'
                });
                $('#permissions-form').append(permField);
            }
        });
    });
    
    // إضافة معرف المسؤول كحقل مخفي
    const adminIdInput = $('<input>').attr({
        type: 'hidden',
        name: 'admin_id',
        value: $('#admin-id').val() || $('form').data('admin-id')
    });
    $('#permissions-form').append(adminIdInput);
}

/**
 * ربط الأزرار العامة
 */
function bindUtilityButtons() {
    // زر فتح جميع البطاقات
    $('#expand-all').on('click', function(e) {
        // منع السلوك الافتراضي
        e.preventDefault();
        e.stopPropagation();
        
        $('.section-body').slideDown();
        showNotification('تم', 'تم فتح جميع البطاقات', 'success');
        
        return false;
    });
    
    // زر فتح/إغلاق محتوى القسم
    $('.toggle-section').on('click', function(e) {
        // منع السلوك الافتراضي
        e.preventDefault();
        e.stopPropagation();
        
        const sectionBody = $(this).closest('.permissions-section').find('.section-body');
        sectionBody.slideToggle();
        
        // تبديل الأيقونة
        const icon = $(this).find('i');
        if (icon.hasClass('fa-chevron-down')) {
            icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
        } else {
            icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
        }
        
        return false;
    });
}

/**
 * تحديث عدد الصلاحيات المفعلة في كل قسم
 */
function updatePermissionCounts() {
    $('.permissions-section').each(function() {
        const sectionId = $(this).attr('id').replace('section-', '');
        const totalCards = $(this).find('.permission-card').length;
        const activeCards = $(this).find('.permission-card.active').length;
        
        // تحديث عداد الصلاحيات في التبويب
        $(`.tab-item[data-section="${sectionId}"] .tab-count`).text(activeCards);
        
        // تحديث عداد الصلاحيات في القسم
        $(this).find('.section-count').text(`${activeCards} / ${totalCards}`);
    });
}

/**
 * عرض إشعار للمستخدم
 */
function showNotification(title, message, type = 'success') {
    // تحديد لون خلفية الإشعار
    let bgColor, color, icon;
    switch (type) {
        case 'success':
            bgColor = '#d1e7dd';
            color = '#0f5132';
            icon = 'fas fa-check-circle';
            break;
        case 'warning':
            bgColor = '#fff3cd';
            color = '#856404';
            icon = 'fas fa-exclamation-triangle';
            break;
        case 'error':
            bgColor = '#f8d7da';
            color = '#842029';
            icon = 'fas fa-times-circle';
            break;
        default:
            bgColor = '#cfe2ff';
            color = '#084298';
            icon = 'fas fa-info-circle';
    }
    
    // إنشاء عنصر الإشعار
    const notificationId = 'notification-' + Date.now();
    const notification = `
        <div id="${notificationId}" class="notification" style="
            position: fixed;
            top: 20px;
            left: 20px;
            max-width: 350px;
            background-color: ${bgColor};
            color: ${color};
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            display: flex;
            align-items: flex-start;
            gap: 10px;
            transform: translateX(-100%);
            opacity: 0;
            transition: all 0.3s ease;
        ">
            <div style="font-size: 1.2rem;"><i class="${icon}"></i></div>
            <div style="flex-grow: 1;">
                <div style="font-weight: 600; margin-bottom: 5px;">${title}</div>
                <div style="font-size: 0.9rem;">${message}</div>
            </div>
            <div style="cursor: pointer; font-size: 1rem;" onclick="$('#${notificationId}').remove();">
                <i class="fas fa-times"></i>
            </div>
        </div>
    `;
    
    // إضافة الإشعار للصفحة
    $('body').append(notification);
    
    // إظهار الإشعار بتأثير حركي
    setTimeout(() => {
        $(`#${notificationId}`).css({
            transform: 'translateX(0)',
            opacity: 1
        });
        
        // إخفاء الإشعار تلقائيًا بعد 5 ثوانٍ
        setTimeout(() => {
            $(`#${notificationId}`).css({
                transform: 'translateX(-100%)',
                opacity: 0
            });
            
            // حذف الإشعار من DOM بعد انتهاء التأثير الحركي
            setTimeout(() => {
                $(`#${notificationId}`).remove();
            }, 300);
        }, 5000);
    }, 10);
}