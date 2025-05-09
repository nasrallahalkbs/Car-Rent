/* 
* سكريبت بطاقات الصلاحيات المتقدمة
* يحتوي على الوظائف اللازمة لإدارة البطاقات والأقسام
*/

$(document).ready(function() {
    // تهيئة الواجهة
    initializePermissionCards();
    
    // التعامل مع نقرات التبويبات
    $('.neo-tab').on('click', function() {
        if ($(this).attr('id') === 'openAllCardsBtn') {
            // فتح جميع محتويات البطاقات
            $('.department-body').show();
            // تغيير أيقونات الأزرار
            $('.toggle-department-btn i').removeClass('fa-chevron-down').addClass('fa-chevron-up');
            return;
        }
        
        if (!$(this).hasClass('active')) {
            const target = $(this).data('target');
            
            // تبديل التبويبات
            $('.neo-tab').removeClass('active');
            $(this).addClass('active');
            
            // إخفاء جميع الأقسام أولاً
            $('.permissions-container [data-section]').removeClass('active');
            // ثم إظهار القسم المحدد فقط
            $(`[data-section="${target}"]`).addClass('active');
            
            // حفظ التبويب المحدد في التخزين المحلي
            localStorage.setItem('selectedPermissionTab', target);
        }
    });
    
    // استعادة التبويب المحدد سابقاً
    const savedTab = localStorage.getItem('selectedPermissionTab');
    if (savedTab) {
        $(`.neo-tab[data-target="${savedTab}"]`).click();
    } else {
        // تفعيل التبويب الأول افتراضياً
        $('.neo-tab[data-target="dashboard"]').click();
    }
    
    // تفعيل/إلغاء بطاقات الصلاحيات
    $('.permission-card').on('click', function() {
        const card = $(this);
        const statusBadge = card.find('.status-badge');
        
        // تبديل حالة البطاقة
        card.toggleClass('active');
        
        // تحديث حالة البطاقة
        if (card.hasClass('active')) {
            statusBadge.removeClass('none');
            // إعادة الحالة السابقة أو تعيين القراءة كافتراضي
            if (!statusBadge.hasClass('read') && !statusBadge.hasClass('write') && !statusBadge.hasClass('admin')) {
                statusBadge.addClass('read');
            }
        } else {
            // عند إلغاء التنشيط، حفظ الحالة وتعيين none
            statusBadge.removeClass('read write admin').addClass('none');
        }
        
        // تحديث العدادات
        updateActiveCounters();
        
        // تفعيل زر الحفظ
        $('.save-permissions-btn').prop('disabled', false);
    });
    
    // تفعيل أزرار فتح وإغلاق الأقسام
    $('.toggle-department-btn').on('click', function() {
        const departmentBody = $(this).closest('.department-card').find('.department-body');
        const icon = $(this).find('i');
        
        departmentBody.slideToggle(200, function() {
            if (departmentBody.is(':visible')) {
                icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
            } else {
                icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
            }
        });
    });
    
    // تفعيل أزرار تحديد الكل في كل قسم
    $('.select-all-btn').on('click', function() {
        const departmentCard = $(this).closest('.department-card');
        const permissionCards = departmentCard.find('.permission-card');
        
        // تحقق من حالة الصلاحيات الحالية
        const allActive = permissionCards.length === permissionCards.filter('.active').length;
        
        if (allActive) {
            // إذا كانت كل الصلاحيات مفعلة، قم بإلغاء تحديد الكل
            permissionCards.removeClass('active');
            permissionCards.find('.status-badge').removeClass('read write admin').addClass('none');
        } else {
            // قم بتفعيل كل الصلاحيات
            permissionCards.addClass('active');
            
            // تعيين نوع الصلاحية المناسب (وفقاً للمعايير الموجودة)
            permissionCards.each(function() {
                const badgeEl = $(this).find('.status-badge');
                badgeEl.removeClass('none');
                
                if (badgeEl.hasClass('read') || badgeEl.hasClass('write') || badgeEl.hasClass('admin')) {
                    // الحفاظ على التصنيف الموجود
                } else {
                    // تعيين القراءة كافتراضي إذا لم يكن مصنف
                    badgeEl.addClass('read');
                }
            });
        }
        
        // تحديث العدادات
        updateActiveCounters();
        
        // تفعيل زر الحفظ
        $('.save-permissions-btn').prop('disabled', false);
    });
});

// وظيفة محدثة لتحديث عدد الصلاحيات النشطة في كل قسم
function updateActiveCounters() {
    $('[data-section]').each(function() {
        const activeCount = $(this).find('.permission-card.active').length;
        const totalCount = $(this).find('.permission-card').length;
        $(this).find('.active-count').text(activeCount);
    });
}

// تهيئة بطاقات الصلاحيات والتأكد من عرضها بشكل صحيح
function initializePermissionCards() {
    // إصلاح مشكلة عدم ظهور البطاقات
    setTimeout(function() {
        // التأكد من أن بطاقة واحدة على الأقل نشطة
        if ($('.permissions-container [data-section].active').length === 0) {
            // تنشيط قسم لوحة التحكم
            $('.permissions-container [data-section="dashboard"]').addClass('active');
            $('.neo-tab[data-target="dashboard"]').addClass('active');
        }
        
        // إظهار محتويات البطاقات بشكل صحيح
        $('.department-body').each(function() {
            $(this).find('.permissions-grid').css('display', 'grid');
        });
        
        // تحديث العدادات
        updateActiveCounters();
    }, 300);
}