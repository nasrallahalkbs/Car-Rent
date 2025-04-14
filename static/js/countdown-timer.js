// العداد التنازلي للحجوزات
(function() {
    // الدالة الرئيسية للعثور على العدادات التنازلية وتهيئتها
    function initializeCountdowns() {
        console.log("تم تحميل صفحة العداد التنازلي");

        // البحث عن صفوف الحجوزات المؤكدة مع دفع معلق
        const pendingPaymentRows = document.querySelectorAll('tr:has(.status-badge.status-confirmed):has(.payment-badge.payment-pending)');
        console.log("تم العثور على " + pendingPaymentRows.length + " صف يحتاج عداد تنازلي");

        if (pendingPaymentRows.length === 0) {
            console.log("لم يتم العثور على أي عداد تنازلي، سيتم محاولة إنشاءها");

            // طريقة ثانية للبحث عن العناصر
            document.querySelectorAll('.payment-warning').forEach(element => {
                const countdownElement = element.querySelector('[id^="countdown-"]');
                if (countdownElement) {
                    // تعيين وقت انتهاء الصلاحية إذا لم يكن معينًا
                    if (!countdownElement.getAttribute('data-expire-time')) {
                        const now = new Date();
                        const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
                        countdownElement.setAttribute('data-expire-time', tomorrow.toISOString());
                    }
                }
            });
        }

        // إنشاء العدادات لكل صف
        pendingPaymentRows.forEach(function(row) {
            const reservationIdElement = row.querySelector('.reservation-id');
            if (!reservationIdElement) return;

            const reservationId = reservationIdElement.textContent.trim().replace('#', '');
            const actionsCell = row.querySelector('td:last-child');
            if (!actionsCell) return;

            // البحث عن عنصر العداد الموجود أو إنشاء عنصر جديد
            let countdownElement = actionsCell.querySelector(`#countdown-${reservationId}`);

            if (!countdownElement) {
                // إنشاء عنصر تحذير الدفع إذا لم يكن موجودًا
                let paymentWarning = actionsCell.querySelector('.payment-warning');
                if (!paymentWarning) {
                    paymentWarning = document.createElement('div');
                    paymentWarning.className = 'payment-warning mt-2';
                    paymentWarning.style.cssText = 'display: block !important; visibility: visible !important; opacity: 1 !important; width: 100%;';

                    const alertHtml = `
                        <div class="alert alert-danger py-2 px-3 mb-0" style="display: block !important; visibility: visible !important; opacity: 1 !important;">
                            <div class="countdown-container d-flex align-items-center justify-content-between">
                                <div>
                                    <i class="fas fa-exclamation-triangle me-1"></i>
                                    <strong>مدة الدفع:</strong>
                                </div>
                                <div id="countdown-${reservationId}" class="countdown-timer me-2" 
                                    style="display: inline-block !important; visibility: visible !important; opacity: 1 !important; z-index: 999; position: relative; background-color: rgba(220, 53, 69, 0.1); padding: 3px 8px; border-radius: 4px; font-weight: bold;" 
                                    data-reservation-id="${reservationId}">
                                    <span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>
                                </div>
                            </div>
                        </div>
                    `;

                    paymentWarning.innerHTML = alertHtml;

                    // إضافة عنصر التحذير بعد أزرار الدفع
                    const paymentButtons = actionsCell.querySelectorAll('.action-button');
                    if (paymentButtons.length > 0) {
                        const lastButton = paymentButtons[paymentButtons.length - 1];
                        lastButton.parentNode.insertBefore(paymentWarning, lastButton.nextSibling);
                    } else {
                        actionsCell.appendChild(paymentWarning);
                    }

                    // تحديث المرجع لعنصر العداد
                    countdownElement = actionsCell.querySelector(`#countdown-${reservationId}`);
                }
            }

            if (countdownElement) {
                // تعيين وقت انتهاء الصلاحية إذا لم يكن معينًا
                if (!countdownElement.getAttribute('data-expire-time')) {
                    const now = new Date();
                    const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
                    countdownElement.setAttribute('data-expire-time', tomorrow.toISOString());
                }
            }
        });

        // تحديث جميع العدادات
        updateAllCountdowns();
    }

    // دالة لتحديث جميع العدادات التنازلية
    function updateAllCountdowns() {
        const countdownElements = document.querySelectorAll('[id^="countdown-"]');

        if (countdownElements.length === 0) {
            console.log("لم يتم العثور على أي عداد تنازلي للعرض");
            return;
        }

        countdownElements.forEach(function(element) {
            updateCountdown(element);
        });
    }

    // دالة لتحديث عداد تنازلي واحد
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
            console.log("لا تتوفر عناصر العرض للعداد #" + reservationId);
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

    // تحديث جميع العدادات كل ثانية
    function startCountdownTimer() {
        setInterval(function() {
            const countdowns = document.querySelectorAll('[id^="countdown-"]');
            if (countdowns.length > 0) {
                updateAllCountdowns();
            } else {
                console.log("لا توجد عدادات لتحديثها");
            }
        }, 1000);
    }

    // محاولة تهيئة العدادات بمجرد تحميل المستند
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initializeCountdowns();
            startCountdownTimer();
        });
    } else {
        // تم تحميل المستند بالفعل
        initializeCountdowns();
        startCountdownTimer();
    }

    // إعادة تهيئة العدادات عند تحديث المحتوى بشكل ديناميكي
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                initializeCountdowns();
            }
        });
    });

    // تهيئة مراقب التغييرات
    const config = { childList: true, subtree: true };
    observer.observe(document.body, config);
})();