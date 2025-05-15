// سكريبت للتحقق من تحميل CSS صفحة إدارة التقارير
document.addEventListener('DOMContentLoaded', function() {
    // التحقق مما إذا كانت صفحة إدارة التقارير
    if (window.location.href.includes('/admin/reports/') || 
        document.getElementById('reports-css')) {
        
        console.log("تحقق من تحميل تنسيقات صفحة إدارة التقارير...");
        
        // التحقق من وجود تنسيقات CSS الأساسية
        const checkStyles = function() {
            // اختبار ما إذا كانت التنسيقات الأساسية موجودة
            const testElement = document.querySelector('.reports-container');
            
            if (testElement) {
                const styles = window.getComputedStyle(testElement);
                const hasStyles = styles.backgroundColor !== 'rgba(0, 0, 0, 0)' && 
                                 styles.backgroundColor !== 'transparent';
                
                if (!hasStyles) {
                    console.log('تنسيقات صفحة إدارة التقارير غير محملة بشكل صحيح، جاري إعادة تحميلها...');
                    reloadStyles();
                } else {
                    console.log('تنسيقات صفحة إدارة التقارير محملة بشكل صحيح');
                    // تخزين معلومات في localStorage للتحقق في المرات القادمة
                    localStorage.setItem('reports_css_loaded', 'true');
                }
            }
        };
        
        // إعادة تحميل التنسيقات
        const reloadStyles = function() {
            const cssLink = document.createElement('link');
            cssLink.rel = 'stylesheet';
            cssLink.href = '/static/css/reports_management.css?v=' + Date.now();
            document.head.appendChild(cssLink);
            
            // تحقق مرة أخرى بعد التحميل
            cssLink.onload = function() {
                setTimeout(checkStyles, 300);
            };
        };
        
        // التحقق بعد تحميل الصفحة
        setTimeout(checkStyles, 500);
        
        // التحقق عند العودة إلى الصفحة
        window.addEventListener('pageshow', function(event) {
            // إذا تمت العودة من الذاكرة المخبأة (bfcache)
            if (event.persisted) {
                console.log("تمت العودة إلى الصفحة من الذاكرة المخبأة، جاري التحقق من التنسيقات...");
                setTimeout(checkStyles, 300);
            }
        });
    }
});