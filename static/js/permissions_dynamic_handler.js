/**
 * معالج الصلاحيات الديناميكي للقالب admin_permissions_dynamic.html
 * 
 * هذا الملف يقوم بتحديث حقل الإدخال المخفي permissions_data
 * بناءً على الصلاحيات التي يحددها المستخدم في واجهة المستخدم
 */

$(document).ready(function() {
    console.log("🔄 تم تحميل معالج الصلاحيات الديناميكي");
    
    // استرجاع بيانات الصلاحيات المحفوظة
    let permissionsData = {};
    try {
        const permissionsJson = $('#permissions_data').val();
        if (permissionsJson) {
            permissionsData = JSON.parse(permissionsJson);
            console.log("📥 تم تحميل بيانات الصلاحيات:", permissionsData);
        }
    } catch (error) {
        console.error("❌ خطأ في تحليل بيانات الصلاحيات:", error);
    }
    
    // تحديث حقل permissions_data استنادًا إلى البطاقات النشطة
    function updatePermissionsData() {
        // إعادة بناء كائن البيانات
        const updatedPermissions = {};
        
        // المرور على كل قسم
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            updatedPermissions[sectionId] = [];
            
            // البحث عن البطاقات النشطة في هذا القسم
            $(this).find('.permission-card.active').each(function() {
                // استخراج اسم الصلاحية من معرف صندوق الاختيار
                const checkbox = $(this).find('input[type="checkbox"]');
                if (checkbox.length > 0) {
                    const fullName = checkbox.attr('name');
                    if (fullName && fullName.includes('_')) {
                        const permName = fullName.split('_')[1];
                        updatedPermissions[sectionId].push(permName);
                    }
                }
            });
        });
        
        // تحديث حقل الإدخال المخفي
        $('#permissions_data').val(JSON.stringify(updatedPermissions));
        console.log("📤 تم تحديث بيانات الصلاحيات:", updatedPermissions);
    }
    
    // إضافة معالج للنقر على بطاقات الصلاحيات
    $('.permission-card').on('click', function(e) {
        // تجاهل النقر إذا كان على عنصر تفاعلي
        if ($(e.target).is('a, button') || $(e.target).parents('a, button').length > 0) {
            return;
        }
        
        // تبديل حالة البطاقة
        $(this).toggleClass('active');
        
        // تحديث صندوق الاختيار
        const checkbox = $(this).find('input[type="checkbox"]');
        if (checkbox.length > 0) {
            checkbox.prop('checked', $(this).hasClass('active'));
        }
        
        // تحديث بيانات الصلاحيات
        updatePermissionsData();
        
        // تحديث العدادات
        updateCounters();
    });
    
    // تحديث عدادات الصلاحيات
    function updateCounters() {
        $('.permissions-section').each(function() {
            const sectionId = $(this).attr('id').replace('section-', '');
            const activeCount = $(this).find('.permission-card.active').length;
            const totalCount = $(this).find('.permission-card').length;
            
            // تحديث عداد القسم
            $(this).find('.section-count').text(`${activeCount} / ${totalCount}`);
            
            // تحديث عداد التبويب
            $(`.tab-item[data-section="${sectionId}"] .tab-count`).text(activeCount);
            
            // تمييز العداد إذا كان هناك صلاحيات نشطة
            if (activeCount > 0) {
                $(`.tab-item[data-section="${sectionId}"] .tab-count`).addClass('active');
            } else {
                $(`.tab-item[data-section="${sectionId}"] .tab-count`).removeClass('active');
            }
        });
    }
    
    // معالج تحديد الكل
    $('#select-all-permissions, .select-all').on('click', function() {
        let sectionSelector = '.permission-card';
        
        // التحقق مما إذا كان الزر خاص بقسم معين
        if ($(this).hasClass('select-all') && $(this).data('section')) {
            const section = $(this).data('section');
            sectionSelector = `#section-${section} .permission-card`;
        }
        
        // تحديد جميع البطاقات في النطاق المحدد
        $(sectionSelector).addClass('active');
        $(sectionSelector).find('input[type="checkbox"]').prop('checked', true);
        
        // تحديث البيانات والعدادات
        updatePermissionsData();
        updateCounters();
    });
    
    // معالج إلغاء تحديد الكل
    $('#deselect-all-permissions').on('click', function() {
        // إلغاء تحديد جميع البطاقات
        $('.permission-card').removeClass('active');
        $('.permission-card input[type="checkbox"]').prop('checked', false);
        
        // تحديث البيانات والعدادات
        updatePermissionsData();
        updateCounters();
    });
    
    // معالج تبديل عرض القسم
    $('.toggle-section').on('click', function() {
        const sectionBody = $(this).closest('.permissions-section').find('.section-body');
        sectionBody.slideToggle(300);
        $(this).find('i').toggleClass('fa-chevron-down fa-chevron-up');
    });
    
    // معالج تبويبات الأقسام
    $('.tab-item:not(.utility)').on('click', function() {
        const section = $(this).data('section');
        
        // إلغاء تنشيط جميع التبويبات وإخفاء جميع الأقسام
        $('.tab-item').removeClass('active');
        $('.permissions-section').removeClass('active').hide();
        
        // تنشيط التبويب والقسم المحدد
        $(this).addClass('active');
        $(`#section-${section}`).addClass('active').show();
    });
    
    // معالج زر فتح الكل
    $('#expand-all').on('click', function() {
        const allClosed = $('.section-body:hidden').length > 0;
        
        if (allClosed) {
            // فتح جميع الأقسام
            $('.section-body').slideDown(300);
            $('.toggle-section i').removeClass('fa-chevron-down').addClass('fa-chevron-up');
            $(this).find('span').text('إغلاق الكل');
        } else {
            // إغلاق جميع الأقسام
            $('.section-body').slideUp(300);
            $('.toggle-section i').removeClass('fa-chevron-up').addClass('fa-chevron-down');
            $(this).find('span').text('فتح الكل');
        }
    });
    
    // تحديث العدادات عند تحميل الصفحة
    updateCounters();
    
    // إضافة معالج إرسال النموذج
    $('#permissions-form').on('submit', function() {
        // التأكد من تحديث بيانات الصلاحيات قبل الإرسال
        updatePermissionsData();
    });
});