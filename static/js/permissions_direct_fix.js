/**
 * إصلاح مباشر وبسيط جداً لمشكلة تحديد الصلاحيات
 * 
 * هذا الملف يستخدم jQuery مباشرة لتنفيذ السلوك المطلوب
 * دون الاعتماد على الملفات السابقة
 */

$(document).ready(function() {
    console.log("⚡ تم تحميل نظام الصلاحيات البسيط والمباشر");
    
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
    
    // تحديث عدادات الصلاحيات
    function updateAllCounters() {
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            const activeCards = $(this).find('.permission-card.active').length;
            
            // تحديث العداد في التبويب
            $(`.tab-item[data-section="${sectionId}"] .tab-count`).text(activeCards);
            
            if (activeCards > 0) {
                $(`.tab-item[data-section="${sectionId}"] .tab-count`).addClass('active');
            } else {
                $(`.tab-item[data-section="${sectionId}"] .tab-count`).removeClass('active');
            }
        });
    }
    
    // إضافة معالج نقر مباشر لجميع البطاقات
    $('.permission-card').on('click', function(e) {
        // توقف النقر إذا كان على زر أو رابط داخل البطاقة
        if ($(e.target).is('a, button') || $(e.target).parents('a, button').length > 0) {
            return;
        }
        
        // تبديل حالة البطاقة
        $(this).toggleClass('active');
        
        // تحديث عداد القسم
        const section = $(this).closest('.permissions-section');
        const sectionId = section.attr('id').replace('section-', '');
        const activeCards = section.find('.permission-card.active').length;
        
        // تحديث العداد في التبويب
        $(`.tab-item[data-section="${sectionId}"] .tab-count`).text(activeCards);
        
        if (activeCards > 0) {
            $(`.tab-item[data-section="${sectionId}"] .tab-count`).addClass('active');
        } else {
            $(`.tab-item[data-section="${sectionId}"] .tab-count`).removeClass('active');
        }
        
        console.log(`${$(this).hasClass('active') ? '✅' : '❌'} تم تبديل حالة الصلاحية`);
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
            let section = '';
            let permission = '';
            
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
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                // إزالة مؤشر التحميل
                $('#loadingOverlay').remove();
                
                if (response.status === 'success') {
                    // تحديث الصلاحيات المحفوظة
                    if (response.permissions) {
                        savedPermissions = response.permissions;
                        
                        // تحديث عنصر الإدخال المخفي
                        $('#saved_permissions_json').val(JSON.stringify(savedPermissions));
                        
                        // تحديث واجهة المستخدم
                        markActiveCards();
                    }
                    
                    // عرض رسالة نجاح
                    $('<div>')
                        .addClass('alert alert-success position-fixed')
                        .css({
                            top: '80px',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            zIndex: 9999,
                            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                            minWidth: '300px'
                        })
                        .html('<i class="fas fa-check-circle me-2"></i> تم حفظ الصلاحيات بنجاح')
                        .appendTo('body')
                        .delay(3000)
                        .fadeOut(500, function() {
                            $(this).remove();
                        });
                } else {
                    // عرض رسالة خطأ
                    $('<div>')
                        .addClass('alert alert-danger position-fixed')
                        .css({
                            top: '80px',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            zIndex: 9999,
                            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                            minWidth: '300px'
                        })
                        .html('<i class="fas fa-exclamation-circle me-2"></i> ' + (response.message || 'حدث خطأ أثناء حفظ الصلاحيات'))
                        .appendTo('body')
                        .delay(4000)
                        .fadeOut(500, function() {
                            $(this).remove();
                        });
                }
            },
            error: function(xhr, status, error) {
                // إزالة مؤشر التحميل
                $('#loadingOverlay').remove();
                
                // عرض رسالة خطأ
                $('<div>')
                    .addClass('alert alert-danger position-fixed')
                    .css({
                        top: '80px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        zIndex: 9999,
                        boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                        minWidth: '300px'
                    })
                    .html('<i class="fas fa-exclamation-circle me-2"></i> حدث خطأ أثناء الاتصال بالخادم')
                    .appendTo('body')
                    .delay(4000)
                    .fadeOut(500, function() {
                        $(this).remove();
                    });
                
                console.error('Error:', error);
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
});