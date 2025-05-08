/**
 * إصلاح مباشر وبسيط جداً لمشكلة تحديد الصلاحيات
 * 
 * هذا الملف يستخدم jQuery مباشرة لتنفيذ السلوك المطلوب
 * دون الاعتماد على الملفات السابقة
 */

$(document).ready(function() {
    console.log("⚡ تم تحميل نظام الصلاحيات المحسن");

    // تخزين الحالة الأولية للصلاحيات
    let initialPermissions = {};
    try {
        const savedJson = $('#saved_permissions_json').val();
        initialPermissions = JSON.parse(savedJson || '{}');
        console.log('✅ تم تحميل الصلاحيات الأولية:', initialPermissions);
    } catch (e) {
        console.error('❌ خطأ في تحميل الصلاحيات الأولية:', e);
    }

    // تحديث البطاقات بناءً على الصلاحيات المحفوظة
    function updateCardsFromPermissions(permissions) {
        // إزالة جميع الفئات النشطة أولاً
        $('.permission-card').removeClass('active');
        
        console.log("🔄 تحديث البطاقات من الصلاحيات:", permissions);

        // تحديث المتغير العام
        window.savedPermissions = permissions;
        
        // حفظ في الحقل المخفي
        $('#saved_permissions_json').val(JSON.stringify(permissions));

        // تحديث البطاقات للأقسام والصلاحيات
        Object.entries(permissions).forEach(([section, perms]) => {
            if (Array.isArray(perms)) {
                perms.forEach(permission => {
                    console.log(`🔹 تنشيط الصلاحية: ${section}.${permission}`);
                    
                    // الطريقة 1: البحث باستخدام السمات
                    const cards = $(`.permission-card[data-section="${section}"][data-permission="${permission}"]`);
                    if (cards.length) {
                        cards.addClass('active');
                        console.log(`✅ تم العثور على ${cards.length} بطاقة باستخدام السمات المباشرة`);
                    } else {
                        console.log(`⚠️ لم يتم العثور على بطاقات باستخدام السمات المباشرة`);
                    }
                    
                    // الطريقة 2: البحث في كل قسم
                    const sectionContainer = $(`#section-${section}`);
                    if (sectionContainer.length) {
                        sectionContainer.find('.permission-card').each(function() {
                            // محاولات متعددة للعثور على البطاقة المطلوبة
                            
                            // أ. باستخدام سمة data-permission
                            if ($(this).data('permission') === permission) {
                                $(this).addClass('active');
                            }
                            
                            // ب. باستخدام العنوان
                            const title = $(this).find('.permission-title');
                            if (title.length && title.data('perm-name') === permission) {
                                $(this).addClass('active');
                            }
                        });
                    }
                });
            }
        });

        // تحديث عدادات الأقسام
        updateAllCounters();
        
        console.log("✅ تم الانتهاء من تحديث البطاقات");
    }

    // جمع الصلاحيات النشطة
    function collectActivePermissions() {
        const permissions = {};

        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            permissions[sectionId] = [];

            $(this).find('.permission-card.active').each(function() {
                const permission = $(this).data('permission');
                if (permission) {
                    permissions[sectionId].push(permission);
                }
            });
        });

        return permissions;
    }

    // معالج حفظ الصلاحيات
    $('#permissionsForm').on('submit', function(e) {
        e.preventDefault();
        savePermissions();
    });

    function savePermissions() {
        const formData = new FormData($('#permissionsForm')[0]);
        const activePermissions = collectActivePermissions();

        // إضافة الصلاحيات النشطة للنموذج
        formData.append('permissions', JSON.stringify(activePermissions));

        // عرض مؤشر التحميل
        const loadingOverlay = $('<div id="loadingOverlay">').css({
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white'
        }).html(`
            <div class="text-center">
                <div class="spinner-border mb-2" role="status"></div>
                <p>جاري حفظ الصلاحيات...</p>
            </div>
        `);

        $('body').append(loadingOverlay);

        // إرسال الطلب
        $.ajax({
            url: $('#permissionsForm').attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log("استجابة الخادم:", response);
                
                if (response.status === 'success') {
                    if (response.permissions) {
                        console.log("الصلاحيات المستلمة من الخادم:", response.permissions);
                        
                        // تحديث الصلاحيات المحفوظة في الحقل المخفي
                        $('#saved_permissions_json').val(JSON.stringify(response.permissions));
                        
                        // تحديث المتغير العام للصلاحيات المحفوظة
                        window.savedPermissions = response.permissions;
                        
                        // تحديث واجهة المستخدم مباشرة
                        updateCardsFromPermissions(response.permissions);
                        
                        // تحديث جميع العدادات
                        updateAllCounters();
                        
                        // تحديث الواجهة يدويًا (إعادة تطبيق الفئات النشطة على البطاقات)
                        markActiveCards();
                    } else {
                        console.warn("لم يتم استلام معلومات الصلاحيات في الاستجابة!");
                        
                        // استرداد الصلاحيات المجمعة
                        const activePermissions = collectActivePermissions();
                        updateCardsFromPermissions(activePermissions);
                    }
                    
                    showNotification('تم', 'تم حفظ الصلاحيات بنجاح', 'success');
                } else {
                    console.error("خطأ في استجابة الخادم:", response);
                    showNotification('خطأ', 'حدث خطأ أثناء حفظ الصلاحيات', 'error');
                }
            },
            error: function(xhr) {
                console.error('خطأ في الحفظ:', xhr);
                showNotification('خطأ', 'حدث خطأ في الاتصال بالخادم', 'error');
            },
            complete: function() {
                $('#loadingOverlay').remove();
            }
        });
    }

    // معالج النقر على البطاقات
    $('.permission-card').on('click', function(e) {
        if (!$(e.target).is('a, button') && !$(e.target).parents('a, button').length) {
            $(this).toggleClass('active');
            updateAllCounters();
        }
    });

    // معالج زر تحديد الكل
    $('.select-all').on('click', function(e) {
        e.preventDefault();
        const section = $(this).data('section');
        $(`#section-${section} .permission-card`).addClass('active');
        updateAllCounters();
    });

    // تحديث عدادات الصلاحيات
    function updateAllCounters() {
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            const totalCards = $(this).find('.permission-card').length;
            const activeCards = $(this).find('.permission-card.active').length;

            // تحديث العداد في التبويب
            $(`.tab-item[data-section="${sectionId}"] .tab-count`)
                .text(activeCards)
                .toggleClass('active', activeCards > 0);

            // تحديث عداد القسم
            $(this).find('.section-count').text(`${activeCards} / ${totalCards}`);
        });
    }

    // تهيئة الواجهة
    updateCardsFromPermissions(initialPermissions);

    // إضافة دالة إظهار الإشعارات المحسنة إذا لم تكن موجودة
    if (typeof showNotification !== 'function') {
        window.showNotification = function(title, message, type = 'success') {
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
                    <button onclick="document.getElementById('${notificationId}').remove()" style="
                        background: none;
                        border: none;
                        cursor: pointer;
                        color: inherit;
                        opacity: 0.7;
                        font-size: 1.2rem;
                        padding: 0;
                        margin-left: 10px;
                    ">×</button>
                </div>
            `;
            
            // إضافة الإشعار إلى الصفحة
            $('body').append(notification);
            
            // تفعيل الإشعار
            setTimeout(() => {
                $(`#${notificationId}`).css({
                    transform: 'translateX(0)',
                    opacity: 1
                });
                
                // إخفاء الإشعار تلقائياً بعد 5 ثوان
                setTimeout(() => {
                    $(`#${notificationId}`).css({
                        transform: 'translateX(-100%)',
                        opacity: 0
                    });
                    
                    // إزالة الإشعار من DOM بعد انتهاء الانتقال
                    setTimeout(() => {
                        $(`#${notificationId}`).remove();
                    }, 300);
                }, 5000);
            }, 100);
        }
    }

    // معالج زر الحفظ
    $('#savePermissionsBtn').on('click', function(e) {
        e.preventDefault();
        savePermissions();
    });

    // إضافة معالج نقر للتبويبات
    $('.tab-item').on('click', function(e) {
        e.preventDefault();

        // تجاهل إذا كان زر فتح الكل
        if ($(this).hasClass('utility')) {
            return;
        }

        const targetSection = $(this).data('section');

        // تحديث حالة التبويبات
        $('.tab-item').removeClass('active');
        $(this).addClass('active');

        // إظهار القسم المطلوب
        $('.permissions-section').removeClass('active');
        $('#section-' + targetSection).addClass('active');

        // إظهار البطاقات في القسم
        $('#section-' + targetSection + ' .section-body').show();

        // تحديث العدادات
        updateAllCounters();
    });

    // معالج فتح/إغلاق الأقسام
    $('.toggle-section').on('click', function(e) {
        e.preventDefault();
        const sectionBody = $(this).closest('.permissions-section').find('.section-body');
        sectionBody.slideToggle();

        // تغيير اتجاه السهم
        const icon = $(this).find('i');
        icon.toggleClass('fa-chevron-down fa-chevron-up');
    });

    // زر فتح جميع الأقسام
    $('#expand-all').on('click', function() {
        $('.section-body').slideDown();
        $('.toggle-section i').removeClass('fa-chevron-down').addClass('fa-chevron-up');
    });

    // تحسين زر تحديد الكل
    $('.select-all').on('click', function(e) {
        e.preventDefault();
        const section = $(this).data('section');
        const cards = $(`#section-${section} .permission-card`);

        // تحديد/إلغاء تحديد البطاقات
        cards.each(function() {
            $(this).addClass('active');
        });

        // تحديث العدادات فقط دون حفظ
        updateAllCounters();
    });


    // تنفيذ تعليم البطاقات النشطة عند تحميل الصفحة
    markActiveCards();
    $('.tab-item:not(.utility)').first().click(); //trigger first tab click after page load

});

// تعليم البطاقات النشطة بناءً على الصلاحيات المحفوظة
function markActiveCards() {
    // إعادة تعيين حالة جميع البطاقات
    $('.permission-card').removeClass('active');

    console.log("🔍 تعليم البطاقات النشطة باستخدام:", window.savedPermissions);

    // تحديد البطاقات النشطة
    for (const section in window.savedPermissions) {
        if (Array.isArray(window.savedPermissions[section])) {
            window.savedPermissions[section].forEach(permission => {
                console.log(`🔸 تعليم الصلاحية: ${section}.${permission}`);
                
                // الطريقة 1: باستخدام سمات البيانات
                $(`.permission-card[data-section="${section}"][data-permission="${permission}"]`).addClass('active');

                // الطريقة 2: باستخدام سمة البيانات على بطاقة الصلاحية
                $(`.permission-card[data-section="${section}"]`).each(function() {
                    const permName = $(this).data('permission');
                    if (permName === permission) {
                        $(this).addClass('active');
                    }
                });

                // الطريقة 3: باستخدام عنوان الصلاحية (احتياطي)
                $(`.permission-card .permission-title[data-perm-name="${permission}"]`).closest('.permission-card').addClass('active');
            });
        }
    }

    // تحديث عدادات الصلاحيات
    updateAllCounters();
    
    console.log("✅ تم الانتهاء من تعليم البطاقات النشطة");
}

// تعريف متغير عام على مستوى النافذة
window.savedPermissions = {};

// تهيئة المتغير العام
$(document).ready(function() {
    try {
        const permissionsJson = $('#saved_permissions_json').val();
        if (permissionsJson) {
            window.savedPermissions = JSON.parse(permissionsJson);
            console.log("✅ تم تحميل الصلاحيات المحفوظة العامة:", window.savedPermissions);
        }
    } catch (error) {
        console.error("❌ خطأ في تحليل الصلاحيات المحفوظة:", error);
    }
});