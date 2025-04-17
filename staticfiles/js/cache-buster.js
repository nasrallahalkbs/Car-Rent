
// وظيفة لإعادة تحميل جميع ملفات CSS لتطبيق التغييرات الجديدة
function reloadStylesheets() {
    const links = document.getElementsByTagName('link');
    for (let i = 0; i < links.length; i++) {
        if (links[i].rel === 'stylesheet') {
            const href = links[i].href.split('?')[0];
            links[i].href = href + '?v=' + new Date().getTime();
        }
    }
    console.log('تم تحديث أوراق الأنماط CSS');
}

// تنفيذ عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // إعادة تحميل أوراق الأنماط كل دقيقة واحدة أثناء التطوير
    reloadStylesheets();
    
    // إضافة زر تحديث مخفي في الزاوية
    const refreshButton = document.createElement('button');
    refreshButton.textContent = 'تحديث الصفحة';
    refreshButton.style.position = 'fixed';
    refreshButton.style.bottom = '10px';
    refreshButton.style.right = '10px';
    refreshButton.style.zIndex = '9999';
    refreshButton.style.padding = '5px 10px';
    refreshButton.style.backgroundColor = '#3a86ff';
    refreshButton.style.color = 'white';
    refreshButton.style.border = 'none';
    refreshButton.style.borderRadius = '4px';
    refreshButton.style.cursor = 'pointer';
    
    refreshButton.addEventListener('click', function() {
        window.location.reload(true); // إعادة تحميل الصفحة بتجاوز ذاكرة التخزين المؤقت
    });
    
    document.body.appendChild(refreshButton);
});
