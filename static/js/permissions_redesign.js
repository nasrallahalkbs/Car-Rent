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
    $('.tab-item').on('click', function() {
        // تجاهل زر فتح الكل لأنه له معالج منفصل
        if ($(this).hasClass('utility')) {
            return;
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
        
        // تفعيل زر الحفظ
        $('.save-button').prop('disabled', false);
    });
    
    // تحديث عداد الصلاحيات المفعلة عند التحميل
    updatePermissionCounts();
}

/**
 * تهيئة أزرار تحديد الكل
 */
function initializeSelectAllButtons() {
    $('.select-all').on('click', function() {
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
        
        // تفعيل جميع أزرار الحفظ
        $('.save-button, .submit-button').prop('disabled', false);
        
        // تأكيد للمستخدم
        showNotification(
            'تم',
            allSelected ? 'تم إلغاء تحديد جميع الصلاحيات' : 'تم تحديد جميع الصلاحيات',
            'success'
        );
    });
}

/**
 * تهيئة زر حفظ التغييرات
 */
function initializeSaveButton() {
    $('.save-button, .submit-button').on('click', function(e) {
        if ($(this).prop('disabled')) {
            return;
        }
        
        // منع السلوك الافتراضي إذا كان الزر من نوع save-button
        if ($(this).hasClass('save-button')) {
            e.preventDefault();
        }
        
        // تعطيل الزر أثناء العملية
        $(this).prop('disabled', true);
        
        // تغيير نص الزر
        const originalText = $(this).html();
        $(this).html('<i class="fas fa-spinner fa-spin"></i> جارِ الحفظ...');
        
        // إضافة حقول مخفية للصلاحيات المختارة
        addHiddenPermissionFields();
        
        // إرسال النموذج
        if ($(this).hasClass('save-button')) {
            $('#permissions-form').submit();
        }
    });
    
    // تحديث زر الحفظ الأساسي عند تغيير الصلاحيات
    $('.permission-card').on('click', function() {
        $('.submit-button').prop('disabled', false);
    });
}

/**
 * إضافة حقول مخفية للصلاحيات المختارة
 */
function addHiddenPermissionFields() {
    // حذف الحقول المخفية السابقة
    $('#permissions-form input[type="hidden"][name^="checkbox_"]').remove();
    $('#permissions-form input[type="hidden"][name$="_view"]').remove();
    $('#permissions-form input[type="hidden"][name$="_edit"]').remove();
    $('#permissions-form input[type="hidden"][name$="_create"]').remove();
    $('#permissions-form input[type="hidden"][name$="_delete"]').remove();
    
    // إضافة حقول مخفية لجميع الصلاحيات المفعلة
    $('.permissions-section').each(function() {
        const sectionId = $(this).attr('id').replace('section-', '');
        
        // إنشاء أسماء حقول للإجراءات القياسية في هذا القسم
        const viewField = sectionId + '_view_' + sectionId;
        const editField = sectionId + '_edit_' + sectionId;
        const createField = sectionId + '_create_' + sectionId;
        const deleteField = sectionId + '_delete_' + sectionId;
        
        // المسح وإعادة إنشاء حقول مخفية لكل صلاحية
        let hasViewPerm = false;
        let hasEditPerm = false;
        let hasCreatePerm = false;
        let hasDeletePerm = false;
        
        // فحص جميع البطاقات النشطة في هذا القسم
        $(this).find('.permission-card').each(function() {
            const permTitle = $(this).find('.permission-title').text().trim();
            const permLevel = $(this).find('.permission-level').text().trim();
            
            // إذا كانت البطاقة نشطة
            if ($(this).hasClass('active')) {
                // تحديد نوع الصلاحية بناءً على النص أو مستوى الصلاحية
                if (permLevel === 'R' || permTitle.indexOf('عرض') !== -1 || permTitle.indexOf('الاطلاع') !== -1) {
                    hasViewPerm = true;
                } else if (permLevel === 'W' || permTitle.indexOf('تعديل') !== -1 || permTitle.indexOf('إضافة') !== -1 || permTitle.indexOf('إنشاء') !== -1) {
                    if (permTitle.indexOf('تعديل') !== -1) {
                        hasEditPerm = true;
                    }
                    if (permTitle.indexOf('إضافة') !== -1 || permTitle.indexOf('إنشاء') !== -1) {
                        hasCreatePerm = true;
                    }
                } else if (permLevel === 'D' || permTitle.indexOf('حذف') !== -1) {
                    hasDeletePerm = true;
                }
                
                // إنشاء حقل مخفي خاص بالبطاقة (للتنوع في أنواع الصلاحيات)
                let fieldName = 'perm_' + permTitle.toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
                const specificField = $('<input>').attr({
                    type: 'hidden',
                    name: sectionId + '_' + fieldName,
                    value: 'on'
                });
                $('#permissions-form').append(specificField);
            }
        });
        
        // إضافة حقول الصلاحيات الرئيسية إذا كانت موجودة
        if (hasViewPerm) {
            const viewInput = $('<input>').attr({
                type: 'hidden',
                name: viewField,
                value: 'on'
            });
            $('#permissions-form').append(viewInput);
        }
        if (hasEditPerm) {
            const editInput = $('<input>').attr({
                type: 'hidden',
                name: editField,
                value: 'on'
            });
            $('#permissions-form').append(editInput);
        }
        if (hasCreatePerm) {
            const createInput = $('<input>').attr({
                type: 'hidden',
                name: createField,
                value: 'on'
            });
            $('#permissions-form').append(createInput);
        }
        if (hasDeletePerm) {
            const deleteInput = $('<input>').attr({
                type: 'hidden',
                name: deleteField,
                value: 'on'
            });
            $('#permissions-form').append(deleteInput);
        }
    });
}

/**
 * ربط الأزرار العامة
 */
function bindUtilityButtons() {
    // زر فتح جميع البطاقات
    $('#expand-all').on('click', function() {
        $('.section-body').slideDown();
        showNotification('تم', 'تم فتح جميع البطاقات', 'success');
    });
    
    // زر فتح/إغلاق محتوى القسم
    $('.toggle-section').on('click', function() {
        const sectionBody = $(this).closest('.permissions-section').find('.section-body');
        sectionBody.slideToggle();
        
        // تبديل الأيقونة
        const icon = $(this).find('i');
        if (icon.hasClass('fa-chevron-down')) {
            icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
        } else {
            icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
        }
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
        
        // إذا كان هناك صلاحيات مفعلة، قم بتفعيل زر الحفظ
        if (activeCards > 0) {
            $('.save-button').prop('disabled', false);
        }
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