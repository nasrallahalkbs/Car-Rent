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
    
    // تتبع التغييرات وتحديث حالة زر الحفظ الثابت
    // تعديل: تم إلغاء إضافة زر حفظ إضافي وتم الاعتماد على زر الحفظ الأساسي فقط
    
    // إضافة مؤشر التغييرات إلى زر الحفظ الحالي إذا لم يكن موجودًا
    if ($('#changes-counter').length === 0) {
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
        
        // إضافة العداد إلى زر الحفظ الحالي
        $('#direct-save-btn').prepend(changesIndicator);
    }
    
    // تحديث عداد التغييرات كل ثانية
    setInterval(() => {
        if (changesCount > 0) {
            // تحديث العداد وإظهار حالة تغيير على زر الحفظ الحالي
            $('#changes-counter').text(changesCount);
            $('#direct-save-btn').addClass('has-changes');
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
                // تحديث الصفحة بعد الحفظ بنجاح
                window.location.reload();
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
        $('#direct-save-btn').addClass('has-changes');
        
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
 * تهيئة زر حفظ التغييرات
 */
function initializeSaveButton() {
    // إضافة معالج نقر لزر الحفظ الرئيسي
    $('#direct-save-btn').on('click', function(e) {
        // نمنع السلوك الافتراضي مؤقتًا لإضافة الحقول الخفية
        e.preventDefault();
        
        console.log('💾 بدء عملية حفظ الصلاحيات...');
        
        // إضافة حقول الصلاحيات المختارة قبل الإرسال
        addHiddenPermissionFields();
        
        // إضافة حقل للإشارة إلى استخدام واجهة مستخدم محسنة
        if (!$('#use-enhanced-ui').length) {
            const enhancedUIField = $('<input>').attr({
                type: 'hidden',
                id: 'use-enhanced-ui',
                name: 'use_enhanced_ui',
                value: 'true'
            });
            $('#permissions-form').append(enhancedUIField);
        }
        
        // عرض إشعار بأنه جاري الحفظ
        showNotification('حفظ', 'جاري حفظ الصلاحيات...', 'info');
        
        // عرض مؤشر جاري الحفظ
        const saveNotificationId = 'direct-save-notification';
        if ($('#' + saveNotificationId).length === 0) {
            const notification = $('<div>').attr({
                id: saveNotificationId,
                class: 'save-indicator'
            }).css({
                position: 'fixed',
                bottom: '70px',
                right: '20px',
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
        }
        
        // استخدام AJAX لحفظ البيانات بدلاً من إعادة تحميل الصفحة
        $.ajax({
            url: $('#permissions-form').attr('action'),
            type: 'POST',
            data: $('#permissions-form').serialize(),
            success: function(response) {
                console.log('✅ تم حفظ الصلاحيات بنجاح');
                
                // تحديث عنصر الصلاحيات المحفوظة إذا كان موجوداً
                if (typeof response === 'object' && response.permissions_json) {
                    console.log('📋 تحديث الصلاحيات المحفوظة:', response.permissions_json);
                    if ($('#saved-permissions').length) {
                        $('#saved-permissions').val(response.permissions_json);
                    } else {
                        const newPermissionsInput = $('<input>').attr({
                            type: 'hidden',
                            id: 'saved-permissions',
                            value: response.permissions_json
                        });
                        $('#permissions-form').append(newPermissionsInput);
                    }
                    
                    // استدعاء تحديث واجهة المستخدم إذا كانت الدالة متاحة
                    if (typeof loadSavedPermissions === 'function') {
                        console.log('🔄 تحديث واجهة المستخدم من البيانات الجديدة');
                        loadSavedPermissions();
                    }
                } else {
                    // إعادة تحميل الصفحة في حالة عدم استلام بيانات أو عدم توفر واجهة مستخدم محسنة
                    console.log('🔄 لم يتم استلام بيانات الصلاحيات، جاري إعادة تحميل الصفحة...');
                    window.location.href = window.location.pathname + '?saved=true';
                    return;
                }
                
                // تحديث إشعار الحفظ
                $('#' + saveNotificationId).html('<i class="fas fa-check-circle"></i> <span>تم حفظ التغييرات بنجاح</span>');
                setTimeout(() => {
                    $('#' + saveNotificationId).fadeOut(300, function() {
                        $(this).remove();
                    });
                }, 2000);
                
                // عرض إشعار نجاح الحفظ
                showNotification('نجاح', 'تم حفظ الصلاحيات بنجاح!', 'success');
                
                // إعادة ضبط عداد التغييرات
                $('#changes-counter').text('0');
                $('#direct-save-btn').removeClass('has-changes');
            },
            error: function(xhr, status, error) {
                console.error('❌ خطأ في حفظ الصلاحيات:', error);
                
                // تحديث إشعار الحفظ لإظهار الخطأ
                $('#' + saveNotificationId).html('<i class="fas fa-exclamation-triangle"></i> <span>حدث خطأ أثناء الحفظ</span>').css('background', '#f44336');
                setTimeout(() => {
                    $('#' + saveNotificationId).fadeOut(300, function() {
                        $(this).remove();
                    });
                }, 3000);
                
                // عرض إشعار خطأ
                showNotification('خطأ', 'حدث خطأ أثناء حفظ الصلاحيات، يرجى المحاولة مرة أخرى', 'error');
                
                // محاولة إعادة تحميل الصفحة في حالة الفشل
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            }
        });
        
        return false; // منع إرسال النموذج تلقائياً
    });
    
    console.log('✅ تم تهيئة زر الحفظ الرئيسي مع دعم AJAX');
}

/**
 * إضافة حقول مخفية للصلاحيات المختارة
 */
function addHiddenPermissionFields() {
    console.log("Adding hidden fields for permissions...");
    
    // حذف الحقول المخفية السابقة
    $('#permissions-form input[type="hidden"][name^="checkbox_"]').remove();
    $('#permissions-form input[type="hidden"][name^="perm_"]').remove();
    $('#permissions-form input[type="hidden"][name$="_view"]').remove();
    $('#permissions-form input[type="hidden"][name$="_edit"]').remove();
    $('#permissions-form input[type="hidden"][name$="_create"]').remove();
    $('#permissions-form input[type="hidden"][name$="_delete"]').remove();
    
    // تخزين الصلاحيات المفعلة
    const activePermissions = {};
    
    // إضافة حقول مخفية لجميع الصلاحيات المفعلة
    $('.permissions-section').each(function() {
        const sectionId = $(this).attr('id').replace('section-', '');
        
        // إنشاء مصفوفة للقسم
        if (!activePermissions[sectionId]) {
            activePermissions[sectionId] = [];
        }
        
        // فحص جميع البطاقات النشطة في هذا القسم
        $(this).find('.permission-card').each(function() {
            const permTitle = $(this).find('.permission-title').text().trim();
            const permName = $(this).find('.permission-title').data('perm-name') || 
                           permTitle.toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
            
            // إذا كانت البطاقة نشطة
            if ($(this).hasClass('active')) {
                // إضافة الصلاحية للمصفوفة
                activePermissions[sectionId].push(permName);
                
                // الطريقة الأساسية: وضع الاسم مباشرة section_permission
                const directField = $('<input>').attr({
                    type: 'hidden',
                    name: sectionId + '_' + permName,
                    value: 'on'
                });
                $('#permissions-form').append(directField);
                
                // تحديد نوع الصلاحية
                const permLevel = $(this).find('.permission-level').text().trim();
                let permType = 'view'; // الافتراضي
                
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
                
                // إنشاء حقول باختلاف الأنماط للتأكد من التوافقية مع المعالج
                // نمط 1: section_type_section
                const typeField = $('<input>').attr({
                    type: 'hidden',
                    name: `${sectionId}_${permType}_${sectionId}`,
                    value: 'on'
                });
                $('#permissions-form').append(typeField);
                
                // نمط 2: section_perm
                const sectionPermField = $('<input>').attr({
                    type: 'hidden',
                    name: `${sectionId}_${permName}`,
                    value: 'on'
                });
                $('#permissions-form').append(sectionPermField);
            }
        });
    });
    
    // إضافة معرف المسؤول كحقل مخفي
    const adminId = $('#admin-id').val() || $('form').data('admin-id');
    const adminIdInput = $('<input>').attr({
        type: 'hidden',
        name: 'admin_id',
        value: adminId
    });
    $('#permissions-form').append(adminIdInput);
    
    // طباعة عدد الصلاحيات المفعلة
    console.log("Active permissions:", activePermissions);
    console.log("Total fields added:", $('#permissions-form input[type="hidden"]').length);
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
        
        // طباعة معلومات تشخيصية
        console.log(`⚡ تحديث عداد القسم (${sectionId}): عدد الصلاحيات النشطة = ${activeCards}`);
        
        // تحديث عداد الصلاحيات في التبويب
        $(`.tab-item[data-section="${sectionId}"] .tab-count`).text(activeCards);
        
        // تحديث عداد الصلاحيات في القسم
        $(this).find('.section-count').text(`${activeCards} / ${totalCards}`);
        
        // تغيير لون العداد إذا كان أكبر من صفر
        if (activeCards > 0) {
            $(`.tab-item[data-section="${sectionId}"] .tab-count`).addClass('active');
        } else {
            $(`.tab-item[data-section="${sectionId}"] .tab-count`).removeClass('active');
            // تأكيد إضافي لتصفير العداد
            $(`.tab-item[data-section="${sectionId}"] .tab-count`).text('0');
            console.log(`🚨 تصفير عداد قسم ${sectionId}`);
        }
    });
    
    // طباعة تفاصيل كاملة عن عدادات قسم الحجوزات
    const reservationCards = $('#section-reservations .permission-card').length;
    const reservationActiveCards = $('#section-reservations .permission-card.active').length;
    console.log(`📊 إحصائيات قسم الحجوزات: إجمالي = ${reservationCards}، نشط = ${reservationActiveCards}`);
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