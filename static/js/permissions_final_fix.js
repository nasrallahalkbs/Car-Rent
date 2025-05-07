/**
 * الحل النهائي لمشكلة CSRF في صفحة الصلاحيات
 * هذا الملف يتبع توصيات Django الرسمية للتعامل مع CSRF
 * يجب استدعاؤه قبل جميع ملفات JavaScript الأخرى
 */

// عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ تم تحميل الحل النهائي للصلاحيات');
    
    // إعداد jQuery لإرسال رمز CSRF مع جميع طلبات AJAX
    function setupAjaxCsrf() {
        // الحصول على رمز CSRF من كوكي 
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        // إعداد AJAX
        const csrftoken = getCookie('csrftoken');
        
        // إضافة رمز CSRF لجميع طلبات AJAX
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        
        console.log('✓ تم إعداد CSRF لجميع طلبات AJAX');
    }
    
    // استخدام النموذج التقليدي لحفظ الصلاحيات والحفاظ على رموز CSRF
    function setupPermissionButtonsTraditional() {
        console.log('⚙️ تنفيذ إعداد أزرار الصلاحيات - الحل النهائي');
        
        // 1. إلغاء السلوك السابق
        $('#save-all-permissions-btn').off('click');
        $('#direct-save-btn').off('click');
        
        // 2. إعادة تعيين سلوك زر الحفظ
        $('#permissions-form').off('submit').on('submit', function(e) {
            // السماح بالإرسال المباشر للنموذج
            console.log('🚀 إرسال النموذج بالطريقة التقليدية');
            
            // تغيير نص أزرار الحفظ
            $('#direct-save-btn').html('<i class="fas fa-spinner fa-spin"></i> جاري الحفظ...');
            $('#save-all-permissions-btn').html('<i class="fas fa-spinner fa-spin"></i> جاري الحفظ...');
            
            // السماح بالإرسال المعتاد
            return true;
        });
        
        // 3. جعل الأزرار الثانوية ترسل النموذج
        $('#save-all-permissions-btn').on('click', function(e) {
            e.preventDefault();
            console.log('👆 النقر على زر حفظ جميع الصلاحيات');
            
            // إرسال النموذج مباشرة
            $('#permissions-form').submit();
        });
        
        $('#direct-save-btn').on('click', function(e) {
            e.preventDefault();
            console.log('👆 النقر على زر حفظ التغييرات');
            
            // إرسال النموذج مباشرة
            $('#permissions-form').submit();
        });
        
        console.log('✓ تم إعداد أزرار الصلاحيات');
    }
    
    // تعديل النموذج لإضافة حقول الصلاحيات النشطة والمطلوبة
    function prepareFormBeforeSubmit() {
        console.log('⚙️ إعداد النموذج قبل الإرسال');
        
        // استبدال وظيفة التقديم في النموذج الأصلي
        $('#permissions-form').off('submit').on('submit', function(e) {
            // توقف مؤقتًا لإعداد الحقول
            e.preventDefault();
            
            // 1. حذف الحقول القديمة
            $(this).find('input[type="hidden"]:not([name="csrfmiddlewaretoken"]):not([name="admin_id"])').remove();
            
            // 2. جمع الصلاحيات النشطة
            $('.permissions-section').each(function() {
                var sectionId = $(this).attr('id').replace('section-', '');
                var activeCount = 0;
                
                // إضافة حقول للصلاحيات النشطة فقط
                $(this).find('.permission-card.active').each(function() {
                    var permName = $(this).find('.permission-title').data('perm-name') || 
                                  $(this).find('.permission-title').text().trim().toLowerCase().replace(/\s+/g, '_').replace(/[^\w\s]/gi, '');
                    
                    // إضافة حقل للصلاحية
                    var hiddenField = $('<input>').attr({
                        type: 'hidden',
                        name: sectionId + '_' + permName,
                        value: 'on'
                    });
                    
                    $('#permissions-form').append(hiddenField);
                    activeCount++;
                });
                
                // إضافة علامة للأقسام الفارغة
                if (activeCount === 0) {
                    var emptyField = $('<input>').attr({
                        type: 'hidden',
                        name: sectionId + '_empty',
                        value: 'true'
                    });
                    $('#permissions-form').append(emptyField);
                }
            });
            
            // 3. إضافة علامة حفظ التغييرات
            $('<input>').attr({
                type: 'hidden',
                name: 'save_changes',
                value: 'save'
            }).appendTo('#permissions-form');
            
            // 4. تغيير نص أزرار الحفظ
            $('#direct-save-btn').html('<i class="fas fa-spinner fa-spin"></i> جاري الحفظ...');
            $('#save-all-permissions-btn').html('<i class="fas fa-spinner fa-spin"></i> جاري الحفظ...');
            
            // 5. متابعة الإرسال باستخدام النموذج الأصلي
            console.log('✓ تم إعداد النموذج بنجاح');
            console.log('🚀 جاري إرسال النموذج');
            this.submit();
        });
        
        console.log('✓ تم إعداد وظيفة تقديم النموذج');
    }
    
    // تنفيذ الإعدادات
    setupAjaxCsrf();
    setupPermissionButtonsTraditional();
    prepareFormBeforeSubmit();
    
    // إضافة مستمع لنقرات البطاقات لتتبع التغييرات
    $('.permission-card').off('click').on('click', function() {
        $(this).toggleClass('active');
        
        // تحديث عداد القسم
        var sectionId = $(this).closest('.permissions-section').attr('id').replace('section-', '');
        var activeCount = $('#section-' + sectionId).find('.permission-card.active').length;
        var totalCount = $('#section-' + sectionId).find('.permission-card').length;
        
        // تحديث عداد العنوان
        $('#section-' + sectionId).find('.section-count').text(activeCount + ' / ' + totalCount);
        
        // تحديث عداد الشريط الجانبي
        $('.tab-item[data-section="' + sectionId + '"] .tab-count').text(activeCount);
        
        // تغيير لون العداد
        if (activeCount > 0) {
            $('.tab-item[data-section="' + sectionId + '"] .tab-count').addClass('active');
        } else {
            $('.tab-item[data-section="' + sectionId + '"] .tab-count').removeClass('active');
        }
    });
    
    console.log('✅ تم تنفيذ الحل النهائي للصلاحيات');
});