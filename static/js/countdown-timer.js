document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");
    setupCountdowns();

    // تحديث العدادات كل ثانية
    setInterval(updateAllCountdowns, 1000);
});

// دالة البحث عن العدادات وتهيئتها
function setupCountdowns() {
    // البحث عن عناصر العداد التنازلي مباشرة
    const countdownElements = document.querySelectorAll('[id^="countdown-"]');
    console.log("تم العثور على " + countdownElements.length + " عداد تنازلي");

    if (countdownElements.length === 0) {
        console.log("لم يتم العثور على أي عداد تنازلي، سيتم محاولة إنشاءها");

        // البحث عن الصفوف التي تحتوي على حجوزات مؤكدة بانتظار الدفع
        const pendingPaymentRows = document.querySelectorAll('tr:has(.status-badge.status-confirmed):has(.payment-badge.payment-pending)');

        if (pendingPaymentRows.length > 0) {
            console.log("تم العثور على " + pendingPaymentRows.length + " صف يحتاج عداد تنازلي");

            pendingPaymentRows.forEach(function(row) {
                createCountdownForRow(row);
            });
        }
    }
}

// إنشاء عداد تنازلي لصف معين
function createCountdownForRow(row) {
    // البحث عن خلية الإجراءات
    const actionsCell = row.querySelector('td:last-child');
    if (!actionsCell) return;

    // البحث عن معرف الحجز
    const idElement = row.querySelector('.reservation-id');
    let reservationId = "unknown";
    if (idElement) {
        reservationId = idElement.textContent.trim().replace('#', '');
    }

    // البحث عن أزرار الدفع للتأكد من أننا في صف صحيح
    const paymentButtons = actionsCell.querySelectorAll('.btn-success, .btn-info');
    if (paymentButtons.length === 0) return;

    // التحقق من وجود عنصر تحذير الدفع بالفعل
    let paymentWarning = actionsCell.querySelector('.payment-warning');

    // إنشاء عنصر تحذير الدفع إذا لم يكن موجوداً
    if (!paymentWarning) {
        // إنشاء عنصر تحذير الدفع
        paymentWarning = document.createElement('div');
        paymentWarning.className = 'payment-warning mt-2';
        paymentWarning.style.cssText = 'display: block !important; visibility: visible !important; opacity: 1 !important; width: 100% !important; margin-top: 10px !important; clear: both !important;';

        // تحديد اتجاه النص
        const isRTL = document.documentElement.dir === 'rtl';

        const alertHtml = `
            <div class="alert alert-danger py-2 px-3 mb-0" style="display: block !important; visibility: visible !important; opacity: 1 !important; width: 100% !important; box-shadow: 0 2px 5px rgba(0,0,0,0.15); border-left: 3px solid #dc3545;">
                <div class="countdown-container d-flex align-items-center justify-content-between" style="width: 100% !important;">
                    <div>
                        <i class="fas fa-exclamation-triangle ${isRTL ? 'ms-1' : 'me-1'}"></i>
                        ${isRTL ? '<strong>مدة الدفع:</strong>' : '<strong>Payment required:</strong>'}
                    </div>

                    <div id="countdown-${reservationId}" class="countdown-timer ${isRTL ? 'me-2' : 'ms-2'}" 
                        style="display: inline-block !important; visibility: visible !important; opacity: 1 !important; z-index: 999 !important; position: relative !important; background-color: rgba(220, 53, 69, 0.1); padding: 3px 8px !important; border-radius: 4px !important; font-weight: bold !important; min-width: 90px !important; text-align: center !important;" 
                        data-reservation-id="${reservationId}">
                        <span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>
                    </div>
                </div>
            </div>
        `;

        paymentWarning.innerHTML = alertHtml;

        // إضافة العنصر بعد أزرار الدفع
        const lastPaymentButton = paymentButtons[paymentButtons.length - 1];
        lastPaymentButton.parentNode.insertBefore(paymentWarning, lastPaymentButton.nextSibling);
    }
}

// تحديث جميع العدادات
function updateAllCountdowns() {
    const countdownElements = document.querySelectorAll('[id^="countdown-"]');

    if (countdownElements.length === 0) {
        console.log("لم يتم العثور على أي عداد تنازلي للعرض");
        return;
    }

    console.log("تحديث " + countdownElements.length + " عداد تنازلي");

    countdownElements.forEach(function(element) {
        updateCountdown(element);
    });
}

// تحديث عداد محدد
function updateCountdown(element) {
    // الحصول على معرف الحجز
    const reservationId = element.getAttribute('data-reservation-id');

    // الحصول على وقت انتهاء الصلاحية
    let expireTimeStr = element.getAttribute('data-expire-time');

    // إذا لم يكن هناك وقت انتهاء الصلاحية، استخدم 24 ساعة من الآن
    if (!expireTimeStr) {
        const now = new Date();
        const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        expireTimeStr = tomorrow.toISOString();
        element.setAttribute('data-expire-time', expireTimeStr);
    }

    const expireTime = new Date(expireTimeStr);
    const now = new Date();

    // حساب الوقت المتبقي
    let remainingTime = expireTime - now;

    // البحث عن عناصر العرض
    const hoursElement = element.querySelector('.hours');
    const minutesElement = element.querySelector('.minutes');
    const secondsElement = element.querySelector('.seconds');

    // التأكد من وجود عناصر العرض
    if (!hoursElement || !minutesElement || !secondsElement) {
        element.innerHTML = '<span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';
        return;
    }

    // إذا انتهى الوقت
    if (remainingTime <= 0) {
        hoursElement.textContent = '00';
        minutesElement.textContent = '00';
        secondsElement.textContent = '00';
        element.classList.add('text-danger');
        return;
    }

    // حساب الساعات والدقائق والثواني
    const hours = Math.floor(remainingTime / (1000 * 60 * 60));
    remainingTime -= hours * (1000 * 60 * 60);

    const minutes = Math.floor(remainingTime / (1000 * 60));
    remainingTime -= minutes * (1000 * 60);

    const seconds = Math.floor(remainingTime / 1000);

    // تغيير لون العداد بناءً على الوقت المتبقي
    if (hours < 2) {
        element.classList.add('text-warning');
    }
    if (hours === 0 && minutes < 30) {
        element.classList.remove('text-warning');
        element.classList.add('text-danger');
    }

    // تحديث العداد
    hoursElement.textContent = hours.toString().padStart(2, '0');
    minutesElement.textContent = minutes.toString().padStart(2, '0');
    secondsElement.textContent = seconds.toString().padStart(2, '0');
}