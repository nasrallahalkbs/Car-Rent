/**
 * إصلاح آمن وموثوق لمشكلة حفظ الصلاحيات المتقدمة CSRF
 * 
 * الإصدار 3.0 - حل نهائي معتمد على AJAX
 */

// استخدام وظيفة معتمدة من Django للحصول على رمز CSRF
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// عند تحميل الصفحة
$(document).ready(function() {
    console.log('⚠️ تنفيذ الإصلاح النهائي باستخدام AJAX...');
    
    // إصلاح أزرار حفظ الصلاحيات
    function fixSaveButtons() {
        console.log('⚙️ إصلاح أزرار الحفظ - التنفيذ النهائي');
        
        // 1. إضافة التعامل مع النقر على زر حفظ كل الصلاحيات
        $('#save-all-permissions-btn').off('click').on('click', function(e) {
            e.preventDefault();
            console.log('👆 تم النقر على زر حفظ جميع الصلاحيات');
            savePermissionsWithAjax();
            return false;
        });
        
        // 2. إضافة التعامل مع النقر على زر حفظ التغييرات
        $('#direct-save-btn').off('click').on('click', function(e) {
            e.preventDefault();
            console.log('👆 تم النقر على زر حفظ التغييرات');
            savePermissionsWithAjax();
            return false;
        });
        
        // 3. العثور على النموذج وإيقاف السلوك الافتراضي
        $('#permissions-form').off('submit').on('submit', function(e) {
            e.preventDefault();
            console.log('👆 تم تقديم النموذج');
            savePermissionsWithAjax();
            return false;
        });
        
        console.log('✅ تم إصلاح أزرار الحفظ');
    }
    
    // دالة حفظ الصلاحيات باستخدام AJAX
    function savePermissionsWithAjax() {
        console.log('⚠️ بدء آلية الحفظ باستخدام AJAX');
        
        // 1. جمع جميع الصلاحيات النشطة حالياً
        var activePermissions = {};
        $('.permissions-section').each(function() {
            var sectionId = $(this).attr('id').replace('section-', '');
            activePermissions[sectionId] = [];
            
            $(this).find('.permission-card.active').each(function() {
                var permName = $(this).find('.permission-title').data('perm-name') || 
                               $(this).find('.permission-title').text().trim().toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
                activePermissions[sectionId].push(permName);
            });
        });
        
        // 2. تغيير نص أزرار الحفظ لتظهر "جاري الحفظ"
        $('#direct-save-btn').html('<i class="fas fa-spinner fa-spin"></i> جاري الحفظ...').prop('disabled', true);
        $('#save-all-permissions-btn').html('<i class="fas fa-spinner fa-spin"></i> جاري الحفظ...').prop('disabled', true);
        
        // 3. الحصول على رمز CSRF من الـ cookie
        var csrftoken = getCookie('csrftoken');
        
        // 4. تجميع بيانات النموذج
        var formData = {};
        
        // إضافة رمز CSRF
        formData['csrfmiddlewaretoken'] = csrftoken;
        
        // إضافة معرف المسؤول
        var adminId = $('#admin-id').val() || $('#permissions-form').data('admin-id');
        formData['admin_id'] = adminId;
        
        // إضافة علامة حفظ التغييرات
        formData['save_changes_only'] = 'true';
        formData['save_changes'] = 'save';
        
        // إضافة JSON التغييرات
        formData['changes_json'] = JSON.stringify(activePermissions);
        
        // إضافة الصلاحيات النشطة
        for (var sectionId in activePermissions) {
            for (var i = 0; i < activePermissions[sectionId].length; i++) {
                var permName = activePermissions[sectionId][i];
                formData[sectionId + '_' + permName] = 'on';
            }
        }
        
        // إضافة علامات الأقسام الفارغة
        $('.permissions-section').each(function() {
            var sectionId = $(this).attr('id').replace('section-', '');
            if ($(this).find('.permission-card.active').length === 0) {
                formData[sectionId + '_empty'] = 'true';
            }
        });
        
        console.log('🚀 إرسال البيانات باستخدام AJAX...');
        
        // 5. إرسال البيانات باستخدام AJAX
        $.ajax({
            url: $('#permissions-form').attr('action'),
            method: 'POST',
            data: formData,
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(response) {
                console.log('✅ تم حفظ الصلاحيات بنجاح!');
                // إعادة تحميل الصفحة أو التحويل إلى صفحة النجاح
                window.location.href = $('#permissions-form').attr('action') + '?saved=true';
            },
            error: function(xhr, status, error) {
                console.error('❌ حدث خطأ أثناء حفظ الصلاحيات:', error);
                // إعادة تفعيل أزرار الحفظ
                $('#direct-save-btn').html('<i class="fas fa-save"></i> حفظ التغييرات').prop('disabled', false);
                $('#save-all-permissions-btn').html('<i class="fas fa-save"></i> حفظ جميع الصلاحيات').prop('disabled', false);
                // عرض رسالة الخطأ
                alert('حدث خطأ أثناء حفظ الصلاحيات: ' + error);
            }
        });
    }
    
    // تنفيذ إصلاح الأزرار
    setTimeout(fixSaveButtons, 500);
    
    // إصلاح إضافي عند اكتمال تحميل الصفحة
    $(window).on('load', function() {
        fixSaveButtons();
    });
    
    console.log('✅ تم تنفيذ إصلاح AJAX للصلاحيات');
});