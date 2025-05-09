/**
 * ملف سريع لإصلاح مشكلة حفظ الصلاحيات
 * يتم استدعاؤه قبل أي ملف جافا سكريبت آخر
 */

// استدعاء عند تحميل الصفحة
$(document).ready(function() {
    console.log('🚀 بدء تشغيل الإصلاح السريع للصلاحيات');
    
    // مستمع أحداث لإصلاح أزرار الحفظ
    function fixSaveButtons() {
        console.log('⚙️ إصلاح أزرار الحفظ');
        
        // إصلاح زر الحفظ الرئيسي
        $('#direct-save-btn').off('click').on('click', function(e) {
            e.preventDefault();
            console.log('🖱️ تم النقر على زر الحفظ الرئيسي');
            
            // استخدام الدالة المباشرة للإرسال
            directSaveChanges();
            
            return false;
        });
        
        // إصلاح زر الحفظ الثانوي (العائم)
        $('#save-all-permissions-btn').off('click').on('click', function(e) {
            e.preventDefault();
            console.log('🖱️ تم النقر على زر الحفظ الثانوي');
            
            directSaveChanges();
            
            return false;
        });
        
        console.log('✅ تم إصلاح أزرار الحفظ');
    }
    
    // دالة حفظ التغييرات بشكل مباشر
    window.directSaveChanges = function() {
        console.log('⚠️ تشغيل آلية الحفظ المباشر والشاملة');
        
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
        
        console.log('🔍 الصلاحيات النشطة:', activePermissions);
        
        // 2. إعادة تعيين النموذج
        var form = $('#permissions-form');
        // حذف جميع الحقول المخفية السابقة مع الاحتفاظ برمز CSRF
        form.find('input[type="hidden"]:not([name="csrfmiddlewaretoken"])').remove();
        
        // 3. إضافة حقل admin_id
        var adminId = $('#admin-id').val() || form.data('admin-id');
        form.append('<input type="hidden" name="admin_id" value="' + adminId + '">');
        
        // 4. إضافة حقول الصلاحيات
        for (var sectionId in activePermissions) {
            for (var i = 0; i < activePermissions[sectionId].length; i++) {
                var permName = activePermissions[sectionId][i];
                form.append('<input type="hidden" name="' + sectionId + '_' + permName + '" value="on">');
            }
        }
        
        // 5. إضافة علامات الأقسام الفارغة
        $('.permissions-section').each(function() {
            var sectionId = $(this).attr('id').replace('section-', '');
            if ($(this).find('.permission-card.active').length === 0) {
                form.append('<input type="hidden" name="' + sectionId + '_empty" value="true">');
                console.log('⚠️ إضافة علامة إفراغ للقسم: ' + sectionId);
            }
        });
        
        // 6. إضافة علامة حفظ التغييرات
        form.append('<input type="hidden" name="save_changes_only" value="true">');
        
        // 7. تغيير نص زر الحفظ
        $('#direct-save-btn').html('<i class="fas fa-spinner fa-spin"></i> جاري الحفظ...').prop('disabled', true);
        $('#save-all-permissions-btn').html('<i class="fas fa-spinner fa-spin"></i> جاري الحفظ...').prop('disabled', true);
        
        // 8. إرسال النموذج مباشرة بطريقة أكثر أماناً
        console.log('🟢 إرسال النموذج الآن');
        
        // ★★★ طريقة جديدة وآمنة تماماً لإرسال النموذج مع CSRF 
        console.log('⚙️ استخدام الإرسال المعزز للنموذج');
        
        // 1. التأكد من وجود رمز CSRF والاحتفاظ به إذا كان موجوداً
        var csrfField = $('#permissions-form input[name="csrfmiddlewaretoken"]');
        var csrfValue = '';
        
        if (csrfField.length > 0) {
            // الطريقة 1: استخدام الرمز الموجود
            csrfValue = csrfField.val();
            console.log('➡️ استخدام رمز CSRF الموجود في النموذج');
        } else {
            // الطريقة 2: البحث عن الرمز في أي مكان في الصفحة
            csrfValue = $('input[name="csrfmiddlewaretoken"]').val();
            console.log('➡️ استخدام رمز CSRF من الصفحة');
        }
        
        // 2. حذف النموذج وإنشاء نموذج جديد بشكل كامل
        var formHTML = '<form id="temp-form" method="POST" action="' + form.attr('action') + '">';
        
        // 3. إضافة رمز CSRF
        if (csrfValue) {
            formHTML += '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrfValue + '">';
        }
        
        // 4. نسخ جميع الحقول المخفية من النموذج الأصلي
        form.find('input[type="hidden"]').each(function() {
            var name = $(this).attr('name');
            var value = $(this).val();
            if (name && name !== 'csrfmiddlewaretoken') {
                formHTML += '<input type="hidden" name="' + name + '" value="' + value + '">';
            }
        });
        
        // 5. إضافة علامة حفظ التغييرات
        formHTML += '<input type="hidden" name="save_changes" value="save">';
        formHTML += '</form>';
        
        // 6. إضافة النموذج الجديد إلى الصفحة
        $('body').append(formHTML);
        
        // 7. إرسال النموذج الجديد
        console.log('✅ إرسال النموذج المعزز');
        $('#temp-form').submit();
        
        return false;
    };
    
    // إصلاح أزرار الحفظ
    setTimeout(fixSaveButtons, 500);
    
    // إصلاح إضافي عند التأكد من تحميل الصفحة بالكامل
    $(window).on('load', function() {
        fixSaveButtons();
    });
    
    console.log('✅ تم تنفيذ الإصلاح السريع للصلاحيات');
});