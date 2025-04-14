
/**
 * ملف العداد التنازلي - يستخدم للعد التنازلي للحجوزات المؤكدة التي تنتظر الدفع
 * تم تحسينه للتأكد من ظهور العداد دائمًا وعمله بشكل صحيح
 */

// تنفيذ الكود عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");
    
    // المحاولة المباشرة للعثور على عناصر التحذير أولاً
    const paymentWarnings = document.querySelectorAll('.payment-warning');
    if (paymentWarnings.length > 0) {
        console.log("تم العثور على " + paymentWarnings.length + " تحذير دفع");
        
        paymentWarnings.forEach(function(warningDiv, index) {
            // البحث عن عناصر البيانات التي قد تحتوي على وقت انتهاء الصلاحية
            const reservationElement = warningDiv.closest('tr');
            let reservationId = "default";
            
            if (reservationElement) {
                // محاولة العثور على معرّف الحجز
                const reservationIdElement = reservationElement.querySelector('.reservation-id');
                if (reservationIdElement) {
                    reservationId = reservationIdElement.textContent.trim().replace('#', '');
                }
            }
            
            // إنشاء أو تحديث عنصر العداد
            let countdownElement = warningDiv.querySelector('[id^="countdown-"]');
            if (!countdownElement) {
                const alertDiv = warningDiv.querySelector('.alert');
                if (alertDiv) {
                    // عنصر العداد غير موجود، نقوم بإنشائه
                    countdownElement = document.createElement('div');
                    countdownElement.id = `countdown-${reservationId}`;
                    countdownElement.className = 'countdown-timer';
                    countdownElement.setAttribute('data-reservation-id', reservationId);
                    
                    // الحصول على توقيت انتهاء الصلاحية - استخدم الوقت الحالي + 24 ساعة كقيمة افتراضية
                    const now = new Date();
                    const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
                    countdownElement.setAttribute('data-expire-time', tomorrow.toISOString());
                    
                    countdownElement.innerHTML = '<span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';
                    
                    // إضافة العداد إلى التحذير
                    alertDiv.appendChild(countdownElement);
                    console.log("تم إنشاء عداد جديد للحجز #" + reservationId);
                }
            } else {
                // العداد موجود بالفعل، نتأكد من أنه مرئي
                countdownElement.style.display = 'inline-block';
                countdownElement.style.visibility = 'visible';
                countdownElement.style.opacity = '1';
                console.log("تم تحديث العداد الموجود للحجز #" + reservationId);
            }
        });
    } else {
        console.log("لم يتم العثور على أي تحذير دفع");
        
        // محاولة ثانية للبحث عن أي عناصر تحتوي على العداد
        const countdownContainers = document.querySelectorAll('.countdown-container, .alert-danger');
        if (countdownContainers.length > 0) {
            console.log("تم العثور على " + countdownContainers.length + " حاوية محتملة للعداد");
            
            countdownContainers.forEach(function(container, index) {
                let reservationId = "default" + index;
                
                // البحث عن معرّف الحجز في أقرب عنصر
                const row = container.closest('tr');
                if (row) {
                    const idElement = row.querySelector('[id^="#"], .reservation-id');
                    if (idElement) {
                        reservationId = idElement.textContent.trim().replace('#', '');
                    }
                }
                
                // إنشاء عنصر العداد إذا لم يكن موجودًا
                if (!container.querySelector('.countdown-timer')) {
                    const countdownElement = document.createElement('div');
                    countdownElement.id = `countdown-${reservationId}`;
                    countdownElement.className = 'countdown-timer';
                    countdownElement.setAttribute('data-reservation-id', reservationId);
                    
                    // توقيت افتراضي
                    const now = new Date();
                    const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
                    countdownElement.setAttribute('data-expire-time', tomorrow.toISOString());
                    
                    countdownElement.innerHTML = '<span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';
                    
                    // إضافة العداد للحاوية
                    container.appendChild(countdownElement);
                    console.log("تم إنشاء عداد في حاوية بديلة للحجز #" + reservationId);
                }
            });
        } else {
            console.log("لم يتم العثور على أي حاويات محتملة للعداد");
        }
    }

    // البحث عن العدادات التي تم إنشاؤها
    const countdownElements = document.querySelectorAll('[id^="countdown-"]');
    console.log("تم العثور على " + countdownElements.length + " عداد تنازلي بعد المحاولات");

    // تحديث العدادات كل ثانية
    setInterval(updateAllCountdowns, 1000);

    // تحديث العدادات عند تحميل الصفحة
    updateAllCountdowns();
});

/**
 * تحديث جميع العدادات التنازلية في الصفحة
 */
function updateAllCountdowns() {
    // البحث عن جميع عناصر العداد التنازلي في الصفحة (للتأكد من التقاط العناصر المضافة ديناميكيًا)
    const countdownElements = document.querySelectorAll('[id^="countdown-"]');
    
    if (countdownElements.length === 0) {
        console.log("لا توجد عدادات لتحديثها");
        return;
    }

    countdownElements.forEach(function(element) {
        updateCountdown(element);
    });
}

/**
 * تحديث عداد تنازلي محدد
 * @param {HTMLElement} countdownElement - عنصر العداد التنازلي
 */
function updateCountdown(countdownElement) {
    // العداد يجب أن يكون مرئيًا دائمًا - تعزيز الظهور
    countdownElement.style.display = 'inline-block';
    countdownElement.style.visibility = 'visible';
    countdownElement.style.opacity = '1';
    countdownElement.style.position = 'relative';
    countdownElement.style.zIndex = '9999';

    // الحصول على وقت انتهاء الصلاحية من خاصية البيانات
    const expireTimeStr = countdownElement.getAttribute('data-expire-time');
    if (!expireTimeStr) {
        // إذا لم يكن هناك وقت انتهاء صلاحية، استخدم 24 ساعة من الآن
        const now = new Date();
        const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        countdownElement.setAttribute('data-expire-time', tomorrow.toISOString());
        return;
    }

    const expireTime = new Date(expireTimeStr);
    const now = new Date();

    // حساب الوقت المتبقي بالميللي ثانية
    let remainingTime = expireTime - now;

    // عناصر العداد التنازلي
    const hoursElement = countdownElement.querySelector('.hours');
    const minutesElement = countdownElement.querySelector('.minutes');
    const secondsElement = countdownElement.querySelector('.seconds');

    // التأكد من وجود عناصر العداد
    if (!hoursElement || !minutesElement || !secondsElement) {
        console.log("لم يتم العثور على عناصر العداد في العنصر:", countdownElement.id);
        // محاولة إنشاء عناصر العداد
        countdownElement.innerHTML = '<span class="hours">00</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';
        
        // الحصول على العناصر مرة أخرى
        const hoursElement = countdownElement.querySelector('.hours');
        const minutesElement = countdownElement.querySelector('.minutes');
        const secondsElement = countdownElement.querySelector('.seconds');
        
        if (!hoursElement || !minutesElement || !secondsElement) {
            return; // لا يمكن إنشاء العناصر
        }
    }

    if (remainingTime <= 0) {
        // وقت انتهاء الصلاحية قد مر
        hoursElement.textContent = '00';
        minutesElement.textContent = '00';
        secondsElement.textContent = '00';

        // تغيير شكل العداد إلى أحمر للإشارة إلى انتهاء الوقت
        countdownElement.classList.remove('text-warning');
        countdownElement.classList.add('text-danger');

        // البحث عن عنصر التنبيه وإضافة فئة للتأثير البصري
        const alertElement = countdownElement.closest('.alert');
        if (alertElement) {
            alertElement.classList.add('expired-alert');
            alertElement.textContent = 'انتهت صلاحية الدفع';
        }

        return;
    }

    // حساب الساعات والدقائق والثواني المتبقية
    const hours = Math.floor(remainingTime / (1000 * 60 * 60));
    remainingTime -= hours * (1000 * 60 * 60);

    const minutes = Math.floor(remainingTime / (1000 * 60));
    remainingTime -= minutes * (1000 * 60);

    const seconds = Math.floor(remainingTime / 1000);

    // تغيير لون العداد بناءً على الوقت المتبقي
    if (hours < 2) {
        countdownElement.classList.add('text-warning');
    }
    if (hours === 0 && minutes < 30) {
        countdownElement.classList.remove('text-warning');
        countdownElement.classList.add('text-danger');
    }

    // تحديث العداد مع تنسيق دائمًا بخانتين
    hoursElement.textContent = hours.toString().padStart(2, '0');
    minutesElement.textContent = minutes.toString().padStart(2, '0');
    secondsElement.textContent = seconds.toString().padStart(2, '0');
}
