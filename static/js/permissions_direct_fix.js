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
    } catch (e) {
        console.error('خطأ في تحميل الصلاحيات الأولية:', e);
    }

    // تحديث البطاقات بناءً على الصلاحيات المحفوظة
    function updateCardsFromPermissions(permissions) {
        $('.permission-card').removeClass('active');
        
        Object.entries(permissions).forEach(([section, perms]) => {
            perms.forEach(permission => {
                $(`.permission-card[data-section="${section}"][data-permission="${permission}"]`).addClass('active');
                $(`.permission-card .permission-title[data-perm-name="${permission}"]`).closest('.permission-card').addClass('active');
            });
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
                const permission = $(this).find('.permission-title').data('perm-name');
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
        
        const formData = new FormData(this);
        const activePermissions = collectActivePermissions();
        
        // إضافة الصلاحيات النشطة للنموذج
        Object.entries(activePermissions).forEach(([section, permissions]) => {
            permissions.forEach(permission => {
                formData.append(`${section}_${permission}`, 'on');
            });
        });

        // عرض مؤشر التحميل
        $('body').append(`
            <div id="loadingOverlay" style="position:fixed;top:0;left:0;width:100%;height:100%;
                background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;
                justify-content:center;color:white">
                <div>
                    <div class="spinner-border" role="status"></div>
                    <p class="mt-2">جاري حفظ الصلاحيات...</p>
                </div>
            </div>
        `);

        // إرسال الطلب
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === 'success' && response.permissions) {
                    // تحديث الصلاحيات المحفوظة
                    $('#saved_permissions_json').val(JSON.stringify(response.permissions));
                    
                    // تحديث واجهة المستخدم
                    updateCardsFromPermissions(response.permissions);
                    
                    // عرض رسالة نجاح
                    showNotification('تم', 'تم حفظ الصلاحيات بنجاح', 'success');
                }
            },
            error: function() {
                showNotification('خطأ', 'حدث خطأ أثناء حفظ الصلاحيات', 'error');
            },
            complete: function() {
                $('#loadingOverlay').remove();
            }
        });
    });

    // تحديث الواجهة عند التحميل
    updateCardsFromPermissions(initialPermissions);

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

    // استعادة الصلاحيات المحفوظة
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

    // تحسين عرض بطاقات الصلاحيات
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

    // تحديث عدادات الصلاحيات
    function updateAllCounters() {
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            const totalCards = $(this).find('.permission-card').length;
            const activeCards = $(this).find('.permission-card.active').length;

            // تحديث العداد في التبويب
            $(`.tab-item[data-section="${sectionId}"] .tab-count`).text(activeCards);

            // تحديث عداد القسم
            $(this).find('.section-count').text(`${activeCards} / ${totalCards}`);

            if (activeCards > 0) {
                $(`.tab-item[data-section="${sectionId}"] .tab-count`).addClass('active');
            } else {
                $(`.tab-item[data-section="${sectionId}"] .tab-count`).removeClass('active');
            }
        });
    }


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

    // إضافة معالج نقر لبطاقات الصلاحيات
    $('.permission-card').on('click', function(e) {
        if ($(e.target).is('a, button') || $(e.target).parents('a, button').length > 0) {
            return;
        }

        $(this).toggleClass('active');
        updateAllCounters();
    });

    // إضافة معالج إرسال النموذج
    $('#permissionsForm').on('submit', function(e) {
        e.preventDefault();

        // عرض مؤشر التحميل
        $('<div id="loadingOverlay">')
            .css({
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
                flexDirection: 'column',
                color: '#fff'
            })
            .html('<div class="spinner-border text-light" role="status"></div><p class="mt-3">جارٍ حفظ الصلاحيات...</p>')
            .appendTo('body');

        // إنشاء FormData جديد
        const formData = new FormData(this);

        // إضافة حقل مخفي للإشارة إلى استخدام الواجهة المحسنة
        formData.append('use_enhanced_ui', 'true');

        // حذف جميع حقول الصلاحيات القديمة
        // ...

        // إضافة الصلاحيات النشطة فقط
        $('.permission-card.active').each(function() {
            var section = '';
            var permission = '';

            // محاولة الحصول على البيانات من سمات البيانات
            if ($(this).attr('data-section') && $(this).attr('data-permission')) {
                section = $(this).attr('data-section');
                permission = $(this).attr('data-permission');
            } else {
                // محاولة استخراج البيانات من عنصر العنوان
                const titleElement = $(this).find('.permission-title');
                if (titleElement.length > 0 && titleElement.attr('data-perm-name')) {
                    permission = titleElement.attr('data-perm-name');

                    // الحصول على القسم من المعرف
                    const parentSection = $(this).closest('.permissions-section');
                    if (parentSection.length > 0) {
                        section = parentSection.attr('id').replace('section-', '');
                    }
                }
            }

            // إضافة الصلاحية إلى النموذج إذا تم العثور على القسم والصلاحية
            if (section && permission) {
                formData.append(`${section}_${permission}`, 'on');
            }
        });

        // إرسال النموذج باستخدام AJAX
        $.ajax({
            url: $('#permissionsForm').attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === 'success') {
                    // تحديث الصلاحيات المحفوظة
                    if (response.permissions) {
                        savedPermissions = response.permissions;
                        $('#saved_permissions_json').val(JSON.stringify(savedPermissions));

                        // إعادة تعليم البطاقات النشطة
                        markActiveCards();

                        // تحديث العدادات
                        updateAllCounters();

                        // تحديث الواجهة بالكامل
                        $('.permission-card').each(function() {
                            const section = $(this).closest('.permissions-section').attr('id').replace('section-', '');
                            const permission = $(this).find('.permission-title').data('perm-name');

                            if (savedPermissions[section] && savedPermissions[section].includes(permission)) {
                                $(this).addClass('active');
                            } else {
                                $(this).removeClass('active');
                            }
                        });
                    }

                    showNotification('تم', 'تم حفظ الصلاحيات بنجاح', 'success');
                } else {
                    showNotification('خطأ', 'حدث خطأ أثناء حفظ الصلاحيات', 'error');
                }
                $('#loadingOverlay').remove();
            },
            error: function() {
                showNotification('خطأ', 'حدث خطأ في الاتصال بالخادم', 'error');
                $('#loadingOverlay').remove();
            }
        });
    });

    // معالج نقر زر الحفظ
    $('#savePermissionsBtn').on('click', function(e) {
        e.preventDefault();
        $('#permissionsForm').submit();
    });

    // تنفيذ تعليم البطاقات النشطة عند تحميل الصفحة
    markActiveCards();
    $('.tab-item:not(.utility)').first().click(); //trigger first tab click after page load

});