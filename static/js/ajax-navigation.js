/**
 * AJAX Navigation Script
 * يسمح بتحديث المحتوى المركزي فقط عند التنقل بدون تحديث القائمة الجانبية أو التسبب بأي حركة
 */

(function($) {
    // نمط التنفيذ الفوري للحفاظ على نطاق خاص للمتغيرات
    'use strict';
    
    // متغيرات عامة
    let contentSelector = '.admin-content .container-fluid'; // منطقة المحتوى التي سيتم تحديثها
    let ajaxNavEnabled = true; // تمكين/تعطيل التنقل بواسطة AJAX
    let currentUrl = window.location.href; // الرابط الحالي للتأكد من عدم تكرار الطلبات
    let loadingIndicator = null; // مؤشر التحميل
    
    // تهيئة النظام
    function init() {
        // تعيين روابط القائمة الجانبية للاستجابة للنقرات
        setupNavLinks();
        
        // إنشاء مؤشر التحميل
        createLoadingIndicator();
        
        // التعامل مع زر الرجوع في المتصفح
        handleBrowserButtons();
    }
    
    // إنشاء مؤشر التحميل
    function createLoadingIndicator() {
        // إنشاء عنصر مؤشر التحميل إذا لم يكن موجوداً بالفعل
        if ($('#ajax-loading-indicator').length === 0) {
            loadingIndicator = $('<div id="ajax-loading-indicator" class="ajax-loading"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
            $('body').append(loadingIndicator);
            
            // إضافة نمط CSS للمؤشر
            let style = `
                <style>
                    .ajax-loading {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(255, 255, 255, 0.7);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        z-index: 9999;
                        opacity: 0;
                        visibility: hidden;
                        transition: opacity 0.2s;
                    }
                    .ajax-loading.show {
                        opacity: 1;
                        visibility: visible;
                    }
                </style>
            `;
            $('head').append(style);
        }
    }
    
    // تهيئة روابط القائمة الجانبية
    function setupNavLinks() {
        // إضافة مستمع أحداث لجميع روابط القائمة الجانبية
        $('.admin-sidebar .nav-link').off('click.ajaxNav').on('click.ajaxNav', function(e) {
            const $link = $(this);
            const url = $link.attr('href');
            
            // تخطي الحدث إذا كان زر Ctrl أو Command مضغوطاً (فتح في تبويب جديد)
            // أو إذا كان الرابط خارجياً أو كان هو نفس الرابط الحالي
            if (e.ctrlKey || e.metaKey || !url || url.startsWith('http') || url === '#' || url === currentUrl) {
                return true;
            }
            
            // منع السلوك الافتراضي للمتصفح
            e.preventDefault();
            
            // تحديث التنقل بواسطة AJAX
            loadPageContent(url);
            
            // تحديد الرابط النشط في القائمة الجانبية
            $('.admin-sidebar .nav-link').removeClass('active');
            $link.addClass('active');
            
            // تحديث الرابط الحالي
            currentUrl = url;
            
            // تحديث تاريخ المتصفح بدون إعادة تحميل
            window.history.pushState({url: url}, document.title, url);
            
            return false;
        });
    }
    
    // التعامل مع أزرار المتصفح (العودة والأمام)
    function handleBrowserButtons() {
        $(window).on('popstate', function(e) {
            if (e.originalEvent.state && e.originalEvent.state.url) {
                loadPageContent(e.originalEvent.state.url);
                currentUrl = e.originalEvent.state.url;
            }
        });
    }
    
    // تحميل محتوى الصفحة بواسطة AJAX
    function loadPageContent(url) {
        // إظهار مؤشر التحميل
        loadingIndicator.addClass('show');
        
        // تحميل المحتوى بواسطة AJAX
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'html',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                // استخراج المحتوى الرئيسي فقط
                const $data = $(data);
                const content = $data.find(contentSelector).html();
                
                // تحديث المحتوى الرئيسي
                $(contentSelector).html(content);
                
                // تحديث عنوان الصفحة
                const newTitle = $data.filter('title').text();
                if (newTitle) {
                    document.title = newTitle;
                }
                
                // تنفيذ أي سكريبتات في المحتوى الجديد
                executeScripts(content);
                
                // إعادة تهيئة عناصر واجهة المستخدم
                reinitializeUIComponents();
                
                // إخفاء مؤشر التحميل بعد الانتهاء
                loadingIndicator.removeClass('show');
                
                // إعادة تهيئة روابط القائمة في المحتوى الجديد
                setupContentLinks();
            },
            error: function(xhr, status, error) {
                console.error('Failed to load page content:', error);
                
                // في حالة حدوث خطأ، إعادة توجيه المتصفح إلى الرابط المطلوب
                window.location.href = url;
            }
        });
    }
    
    // تنفيذ السكريبتات الموجودة في المحتوى الجديد
    function executeScripts(html) {
        const scriptRegex = /<script\b[^>]*>([\s\S]*?)<\/script>/gm;
        let match;
        
        while (match = scriptRegex.exec(html)) {
            const scriptContent = match[1];
            if (scriptContent) {
                try {
                    eval(scriptContent);
                } catch (e) {
                    console.error('Error executing script:', e);
                }
            }
        }
    }
    
    // إعادة تهيئة مكونات واجهة المستخدم بعد تحميل المحتوى الجديد
    function reinitializeUIComponents() {
        // إعادة تهيئة التلميحات
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            $('[data-bs-toggle="tooltip"]').tooltip();
        }
        
        // إعادة تهيئة النوافذ المنبثقة
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            $('.modal').each(function() {
                new bootstrap.Modal(this);
            });
        }
        
        // أي مكونات إضافية يجب إعادة تهيئتها
    }
    
    // إعادة تهيئة الروابط في المحتوى الجديد
    function setupContentLinks() {
        $(contentSelector).find('a').not('[target="_blank"]').not('[href^="http"]').not('[href^="#"]').on('click', function(e) {
            const url = $(this).attr('href');
            
            // تخطي الحدث إذا كان زر Ctrl أو Command مضغوطاً (فتح في تبويب جديد)
            if (e.ctrlKey || e.metaKey || !url || url === '#') {
                return true;
            }
            
            // منع السلوك الافتراضي للمتصفح
            e.preventDefault();
            
            // تحميل المحتوى الجديد
            loadPageContent(url);
            
            // تحديث تاريخ المتصفح
            window.history.pushState({url: url}, document.title, url);
            
            // تحديد الرابط النشط في القائمة الجانبية إذا كان موجوداً
            $('.admin-sidebar .nav-link').removeClass('active');
            $('.admin-sidebar .nav-link[href="' + url + '"]').addClass('active');
            
            // تحديث الرابط الحالي
            currentUrl = url;
            
            return false;
        });
    }
    
    // تعيين مناطق المحتوى التي سيتم تحديثها
    $.ajaxNavigation = function(options) {
        if (options && options.contentSelector) {
            contentSelector = options.contentSelector;
        }
        
        if (options && typeof options.enabled !== 'undefined') {
            ajaxNavEnabled = options.enabled;
        }
        
        // بدء النظام إذا كان ممكناً
        if (ajaxNavEnabled) {
            init();
        }
        
        return {
            loadPage: loadPageContent,
            reinitialize: init,
            enable: function() { ajaxNavEnabled = true; init(); },
            disable: function() { ajaxNavEnabled = false; }
        };
    };
    
    // عند تحميل المستند، تهيئة النظام
    $(document).ready(function() {
        // حفظ الحالة الأولية في تاريخ المتصفح
        if (window.history && window.history.pushState) {
            window.history.pushState({url: window.location.href}, document.title, window.location.href);
        }
    });
    
})(jQuery);