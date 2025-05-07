/**
 * إصلاح نهائي لمشكلة حفظ الصلاحيات المتقدمة للمسؤولين
 * 
 * هذا الملف يقوم بحل مشكلة عدم حفظ الصلاحيات بسبب خطأ في رمز CSRF
 * ويتعامل مباشرة مع النموذج لضمان إرسال رمز CSRF صالح مع كل طلب
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('📋 تشغيل مُصلِح الصلاحيات المتقدمة v2.0');
    
    // الحصول على رمز CSRF من الميتا
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    
    if (csrfToken) {
        console.log('🔑 تم العثور على رمز CSRF: ' + csrfToken.substring(0, 5) + '...');
    } else {
        console.warn('⚠️ تحذير: لم يتم العثور على رمز CSRF في وسوم الميتا');
    }
    
    // الحصول على رمز CSRF من النموذج
    const csrfInputField = document.querySelector('input[name="csrfmiddlewaretoken"]');
    
    if (csrfInputField) {
        console.log('🔐 تم العثور على حقل CSRF في النموذج: ' + csrfInputField.value.substring(0, 5) + '...');
    } else {
        console.warn('⚠️ تحذير: لم يتم العثور على حقل CSRF في النموذج');
    }
    
    // الحصول على النموذج
    const permissionsForm = document.getElementById('permissions-form');
    
    if (!permissionsForm) {
        console.error('❌ خطأ: لم يتم العثور على نموذج الصلاحيات');
        return;
    }
    
    // التأكد من وجود حقل CSRF في النموذج
    if (!csrfInputField && csrfToken) {
        console.log('➕ إضافة حقل CSRF إلى النموذج');
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = csrfToken;
        
        permissionsForm.prepend(input);
        console.log('✅ تم إضافة حقل CSRF بنجاح');
    } else if (csrfInputField && csrfToken && csrfInputField.value !== csrfToken) {
        console.log('🔄 تحديث قيمة رمز CSRF في النموذج');
        csrfInputField.value = csrfToken;
    }
    
    // الحصول على أزرار الحفظ
    const saveButtons = document.querySelectorAll('.save-permissions-btn');
    
    if (saveButtons.length === 0) {
        console.warn('⚠️ تحذير: لم يتم العثور على أزرار حفظ');
    } else {
        console.log(`🔘 تم العثور على ${saveButtons.length} زر حفظ`);
    }
    
    // إضافة مستمع لأحداث النقر على أزرار الحفظ
    saveButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            console.log('💾 النقر على زر الحفظ');
            
            // التحقق من وجود حقل CSRF قبل الإرسال
            const formCsrfField = document.querySelector('input[name="csrfmiddlewaretoken"]');
            
            if (!formCsrfField) {
                console.error('❌ خطأ: حقل CSRF مفقود قبل الإرسال');
                
                // محاولة إصلاح المشكلة
                if (csrfToken) {
                    console.log('🔧 محاولة إصلاح: إضافة حقل CSRF مباشرة قبل الإرسال');
                    
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'csrfmiddlewaretoken';
                    input.value = csrfToken;
                    
                    permissionsForm.prepend(input);
                    console.log('✅ تم إضافة حقل CSRF بنجاح');
                } else {
                    // محاولة الحصول على الرمز من الكوكيز
                    const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
                    if (csrfCookie) {
                        const csrfFromCookie = csrfCookie.split('=')[1];
                        console.log('🍪 استخدام رمز CSRF من الكوكيز: ' + csrfFromCookie.substring(0, 5) + '...');
                        
                        const input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = 'csrfmiddlewaretoken';
                        input.value = csrfFromCookie;
                        
                        permissionsForm.prepend(input);
                        console.log('✅ تم إضافة حقل CSRF من الكوكيز بنجاح');
                    } else {
                        console.error('❌ فشل الإصلاح: لا يمكن العثور على رمز CSRF');
                        alert('خطأ: حدثت مشكلة في حفظ الصلاحيات، يرجى تحديث الصفحة وإعادة المحاولة');
                        return;
                    }
                }
            }
            
            // محاولة حفظ النموذج
            try {
                console.log('📤 إرسال النموذج...');
                permissionsForm.submit();
            } catch (error) {
                console.error('❌ خطأ في إرسال النموذج:', error);
                
                // محاولة إرسال النموذج يدويًا باستخدام AJAX
                console.log('🔄 محاولة إرسال النموذج باستخدام AJAX...');
                
                const formData = new FormData(permissionsForm);
                
                fetch(permissionsForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                })
                .then(response => {
                    if (response.ok) {
                        console.log('✅ تم الحفظ بنجاح!');
                        window.location.href = permissionsForm.action + '?saved=true';
                    } else {
                        console.error('❌ فشل الحفظ:', response.status);
                        alert('حدث خطأ أثناء حفظ الصلاحيات. يرجى تحديث الصفحة والمحاولة مرة أخرى.');
                    }
                })
                .catch(error => {
                    console.error('❌ خطأ في طلب AJAX:', error);
                    alert('حدث خطأ في الاتصال بالخادم. يرجى التحقق من اتصالك بالإنترنت والمحاولة مرة أخرى.');
                });
            }
        });
    });
    
    // تبديل حالة كل صلاحيات القسم
    const sectionToggles = document.querySelectorAll('.toggle-section');
    
    sectionToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const section = this.dataset.section;
            const checkboxes = document.querySelectorAll(`input[type="checkbox"][id^="${section}_"]`);
            const isActive = this.classList.contains('active');
            
            // تبديل حالة الزر
            if (isActive) {
                this.classList.remove('active');
                this.innerHTML = '<i class="fas fa-toggle-off"></i> تفعيل الكل';
            } else {
                this.classList.add('active');
                this.innerHTML = '<i class="fas fa-toggle-on"></i> تعطيل الكل';
            }
            
            // تغيير حالة جميع خانات الاختيار
            checkboxes.forEach(checkbox => {
                checkbox.checked = !isActive;
                
                // إطلاق حدث التغيير لتحديث العدادات
                const event = new Event('change');
                checkbox.dispatchEvent(event);
            });
        });
    });
    
    console.log('✅ تم تهيئة مُصلِح الصلاحيات المتقدمة بنجاح');
});