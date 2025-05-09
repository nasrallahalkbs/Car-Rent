/**
 * سكربت التأثيرات الإضافية لصفحة تفاصيل السيارة
 */
document.addEventListener('DOMContentLoaded', function() {
    // إضافة تأثيرات عند التمرير
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    // تأثيرات الظهور عند التمرير
    const appearOnScroll = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // تطبيق التأثيرات على أقسام الصفحة
    document.querySelectorAll('.car-detail-panel, .reservation-card, .direct-booking-form').forEach(el => {
        appearOnScroll.observe(el);
    });
    
    // تحسين تجربة حقول التاريخ
    const today = new Date();
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // تعيين الحد الأدنى للتاريخ ليكون اليوم الحالي
        input.min = today.toISOString().split('T')[0];
        
        // إضافة تأثير عند التركيز
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('is-focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('is-focused');
        });
    });
    
    // تحسين عرض المعلومات
    const specItems = document.querySelectorAll('.spec-item');
    specItems.forEach((item, index) => {
        // إضافة تأخير مختلف لكل عنصر
        item.style.animationDelay = `${0.1 + (index * 0.05)}s`;
    });
    
    // تحسين التفاعل مع الأزرار
    const actionButtons = document.querySelectorAll('.action-button');
    actionButtons.forEach(button => {
        button.addEventListener('mouseover', function() {
            this.classList.add('pulse');
        });
        
        button.addEventListener('animationend', function() {
            this.classList.remove('pulse');
        });
    });
    
    // تأثير التحميل اللطيف
    setTimeout(() => {
        document.body.classList.add('content-loaded');
    }, 500);
});

// تحسين حساب السعر الإجمالي
function calculateTotalPrice(startDate, endDate, dailyRate) {
    if (!startDate || !endDate) return 0;
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // التحقق من صحة التواريخ
    if (isNaN(start.getTime()) || isNaN(end.getTime())) return 0;
    
    // حساب عدد الأيام
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    // تحسين عرض عدد الأيام بالعربية
    const daysText = diffDays === 1 ? 'يوم واحد' : 
                     diffDays === 2 ? 'يومان' : 
                     diffDays > 10 ? `${diffDays} يوم` : 
                     `${diffDays} أيام`;
    
    document.getElementById('direct-booking-days').textContent = daysText;
    
    // حساب السعر الإجمالي مع تنسيق العملة
    const totalPrice = diffDays * parseFloat(dailyRate);
    document.getElementById('direct-booking-total').textContent = `${totalPrice.toFixed(2)} د.ك`;
    
    return totalPrice;
}
