/**
 * ملف العداد التنازلي - يستخدم للعد التنازلي للحجوزات المؤكدة التي تنتظر الدفع
 * تم تحسينه للتأكد من ظهور العداد دائمًا وعمله بشكل صحيح
 */

// تنفيذ الكود عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");

    // البحث عن جميع عناصر العداد التنازلي في الصفحة
    const countdownElements = document.querySelectorAll('[id^="countdown-"]');
    console.log("تم العثور على " + countdownElements.length + " عداد تنازلي");

    if (countdownElements.length === 0) {
        console.log("لم يتم العثور على أي عداد تنازلي، سيتم محاولة إنشاءها");

        // البحث عن عناصر قد تحتوي على عدادات
        const paymentWarnings = document.querySelectorAll('.payment-warning');
        if (paymentWarnings.length > 0) {
            paymentWarnings.forEach(function(warningDiv, index) {
                // البحث عن عناصر البيانات التي قد تحتوي على وقت انتهاء الصلاحية
                const reservationElement = warningDiv.closest('tr');
                if (reservationElement) {
                    // محاولة العثور على معرّف الحجز
                    const reservationIdElement = reservationElement.querySelector('.reservation-id');
                    if (reservationIdElement) {
                        const reservationId = reservationIdElement.textContent.replace('#', '');

                        // إنشاء عنصر عداد جديد إذا لم يكن موجودًا
                        let countdownElement = warningDiv.querySelector('[id^="countdown-"]');
                        if (!countdownElement) {
                            const alertDiv = warningDiv.querySelector('.alert');
                            if (alertDiv) {
                                const countdownDiv = document.createElement('div');
                                countdownDiv.id = `countdown-${reservationId}`;
                                countdownDiv.className = 'countdown-timer';
                                countdownDiv.setAttribute('data-reservation-id', reservationId);

                                // الحصول على توقيت انتهاء الصلاحية - استخدم الوقت الحالي + 24 ساعة كقيمة افتراضية
                                const now = new Date();
                                const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
                                countdownDiv.setAttribute('data-expire-time', tomorrow.toISOString());

                                countdownDiv.innerHTML = '<span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';

                                // إضافة العداد إلى التحذير
                                alertDiv.appendChild(countdownDiv);
                                console.log("تم إنشاء عداد جديد للحجز #" + reservationId);
                            }
                        }
                    }
                }
            });
        } else {
            console.log("لم يتم العثور على أي عداد تنازلي للعرض");
        }
    }

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

    countdownElements.forEach(function(element) {
        updateCountdown(element);
    });
}

/**
 * تحديث عداد تنازلي محدد
 * @param {HTMLElement} countdownElement - عنصر العداد التنازلي
 */
function updateCountdown(countdownElement) {
    // العداد يجب أن يكون مرئيًا دائمًا
    countdownElement.style.display = 'inline-block';
    countdownElement.style.visibility = 'visible';
    countdownElement.style.opacity = '1';

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
        return;
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