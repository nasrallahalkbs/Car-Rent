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
        $('.permission-card').removeClass('active');

        Object.entries(permissions).forEach(([section, perms]) => {
            if (Array.isArray(perms)) {
                perms.forEach(permission => {
                    const card = $(`.permission-card[data-section="${section}"][data-permission="${permission}"]`);
                    if (card.length) {
                        card.addClass('active');
                    }
                });
            }
        });

        updateAllCounters();
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
                if (response.status === 'success') {
                    if (response.permissions) {
                        // تحديث الصلاحيات المحفوظة
                        $('#saved_permissions_json').val(JSON.stringify(response.permissions));
                        // تحديث واجهة المستخدم
                        updateCardsFromPermissions(response.permissions);
                    }
                    showNotification('تم', 'تم حفظ الصلاحيات بنجاح', 'success');
                } else {
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

    // تحديد البطاقات النشطة
    for (const section in savedPermissions) {
        if (Array.isArray(savedPermissions[section])) {
            savedPermissions[section].forEach(permission => {
                // الطريقة 1: باستخدام سمات البيانات
                $(`.permission-card[data-section="${section}"][data-permission="${permission}"]`).addClass('active');

                // الطريقة 2: باستخدام عنوان الصلاحية
                $(`.permission-card .permission-title[data-perm-name="${permission}"]`).closest('.permission-card').addClass('active');
            });
        }
    }

    // تحديث العدادات
    updateAllCounters();
}

let savedPermissions = {};
    try {
        const permissionsJson = $('#saved_permissions_json').val();
        if (permissionsJson) {
            savedPermissions = JSON.parse(permissionsJson);
            console.log("✅ تم تحميل الصلاحيات المحفوظة:", savedPermissions);
        }
    } catch (error) {
        console.error("❌ خطأ في تحليل الصلاحيات المحفوظة:", error);
    }