/**
 * ملف JavaScript مبسط للغاية للتعامل مع بطاقات الصلاحيات
 */

$(document).ready(function() {
    console.log("🔄 تم تشغيل البرنامج المبسط للصلاحيات");
    
    // المتغيرات العامة
    var formChanged = false;
    
    // إضافة معالج النقر لبطاقات الصلاحيات
    $('.permission-card').on('click', function() {
        $(this).toggleClass('active');
        formChanged = true;
        
        // تحديث عداد القسم
        var section = $(this).closest('.permissions-section').attr('id').replace('section-', '');
        updateSectionCounter(section);
        
        console.log("تم النقر على الصلاحية:", section);
    });
    
    // إضافة أحداث تفاعلية للتبويبات
    $('.tab-item').on('click', function() {
        var section = $(this).attr('data-section');
        
        // إخفاء جميع الأقسام
        $('.permissions-section').hide();
        
        // إزالة الفئة النشطة من جميع التبويبات
        $('.tab-item').removeClass('active');
        
        // إظهار القسم المحدد وتنشيط التبويب
        $('#section-' + section).show();
        $(this).addClass('active');
    });
    
    // تنشيط أول تبويب افتراضيًا
    $('.tab-item:first').click();
    
    // وظيفة لتحديث عداد صلاحيات القسم
    function updateSectionCounter(section) {
        var activeCount = $('#section-' + section + ' .permission-card.active').length;
        $('.tab-item[data-section="' + section + '"] .tab-count').text(activeCount);
        
        if (activeCount > 0) {
            $('.tab-item[data-section="' + section + '"] .tab-count').addClass('active');
        } else {
            $('.tab-item[data-section="' + section + '"] .tab-count').removeClass('active');
        }
    }
    
    // تحديث جميع عدادات الأقسام
    function updateAllCounters() {
        $('.permissions-section').each(function() {
            var section = $(this).attr('id').replace('section-', '');
            updateSectionCounter(section);
        });
    }
    
    // معالج نموذج حفظ الصلاحيات
    $('#permissionsForm').on('submit', function(e) {
        e.preventDefault();
        
        // إظهار مؤشر التحميل
        showLoading();
        
        // جمع الصلاحيات النشطة وإضافتها إلى النموذج
        var formData = new FormData(this);
        
        // إزالة جميع حقول الصلاحيات الموجودة
        for (var pair of formData.entries()) {
            if (pair[0].indexOf('_') > -1 && pair[0] !== 'csrfmiddlewaretoken' && pair[0] !== 'admin_id') {
                formData.delete(pair[0]);
            }
        }
        
        // إضافة الصلاحيات النشطة فقط
        $('.permission-card.active').each(function() {
            var section = $(this).closest('.permissions-section').attr('id').replace('section-', '');
            var permission = $(this).find('.permission-title').attr('data-perm-name');
            
            if (section && permission) {
                formData.append(section + '_' + permission, 'on');
            }
        });
        
        // إرسال النموذج باستخدام AJAX
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                hideLoading();
                showSuccessMessage('تم حفظ الصلاحيات بنجاح.');
                formChanged = false;
            },
            error: function() {
                hideLoading();
                showErrorMessage('حدث خطأ أثناء حفظ الصلاحيات.');
            }
        });
    });
    
    // عند النقر على زر الحفظ
    $('#savePermissionsBtn').on('click', function(e) {
        e.preventDefault();
        $('#permissionsForm').submit();
    });
    
    // وظائف مساعدة لعرض/إخفاء مؤشر التحميل
    function showLoading() {
        var loadingHtml = '<div id="loadingOverlay" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:9999;display:flex;align-items:center;justify-content:center;">' +
                         '<div style="text-align:center;color:white;">' +
                         '<div class="spinner-border text-light" role="status"></div>' +
                         '<p class="mt-2">جارٍ حفظ الصلاحيات...</p>' +
                         '</div></div>';
        $('body').append(loadingHtml);
    }
    
    function hideLoading() {
        $('#loadingOverlay').remove();
    }
    
    // وظائف مساعدة لعرض رسائل النجاح/الخطأ
    function showSuccessMessage(message) {
        var alertHtml = '<div class="alert alert-success" style="position:fixed;top:80px;left:50%;transform:translateX(-50%);z-index:9999;">' +
                       '<i class="fas fa-check-circle me-2"></i> ' + message +
                       '</div>';
        var $alert = $(alertHtml).appendTo('body');
        setTimeout(function() {
            $alert.fadeOut(500, function() {
                $(this).remove();
            });
        }, 3000);
    }
    
    function showErrorMessage(message) {
        var alertHtml = '<div class="alert alert-danger" style="position:fixed;top:80px;left:50%;transform:translateX(-50%);z-index:9999;">' +
                       '<i class="fas fa-exclamation-circle me-2"></i> ' + message +
                       '</div>';
        var $alert = $(alertHtml).appendTo('body');
        setTimeout(function() {
            $alert.fadeOut(500, function() {
                $(this).remove();
            });
        }, 3000);
    }
    
    // تحديث جميع العدادات عند تحميل الصفحة
    updateAllCounters();
});