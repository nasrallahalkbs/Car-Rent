
/**
 * ملف العداد التنازلي - يستخدم للعد التنازلي للحجوزات المؤكدة التي تنتظر الدفع
 */

// تنفيذ الكود عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");
    
    // البحث عن عناصر العداد في الصفحة
    initializeCountdowns();
    
    // تحديث العدادات كل ثانية
    setInterval(updateAllCountdowns, 1000);
    
    // تحديث العدادات عند تحميل الصفحة
    updateAllCountdowns();
});

/**
 * تهيئة جميع العدادات في الصفحة
 */
function initializeCountdowns() {
    // البحث عن تحذيرات الدفع
    const paymentWarnings = document.querySelectorAll('.payment-warning');
    console.log("تم العثور على " + paymentWarnings.length + " تحذير دفع");
    
    if (paymentWarnings.length > 0) {
        // معالجة كل تحذير دفع
        paymentWarnings.forEach(function(warningDiv) {
            // البحث عن معرف الحجز
            const reservationRow = warningDiv.closest('tr');
            let reservationId = "unknown";
            
            if (reservationRow) {
                const idElement = reservationRow.querySelector('.reservation-id');
                if (idElement) {
                    reservationId = idElement.textContent.trim().replace('#', '');
                }
            }
            
            // البحث عن عنصر التنبيه
            const alertDiv = warningDiv.querySelector('.alert');
            if (!alertDiv) {
                console.log("لم يتم العثور على عنصر التنبيه في تحذير الدفع");
                return;
            }
            
            // البحث عن حاوية العداد
            let countdownContainer = alertDiv.querySelector('.countdown-container');
            if (!countdownContainer) {
                // إنشاء حاوية العداد إذا لم تكن موجودة
                countdownContainer = document.createElement('div');
                countdownContainer.className = 'countdown-container d-flex align-items-center justify-content-between';
                alertDiv.appendChild(countdownContainer);
            }
            
            // البحث عن عنصر النص
            let textElement = countdownContainer.querySelector('div');
            if (!textElement) {
                textElement = document.createElement('div');
                textElement.innerHTML = '<i class="fas fa-exclamation-triangle ms-1"></i> <strong>مدة الدفع:</strong>';
                countdownContainer.appendChild(textElement);
            }
            
            // البحث عن عنصر العداد
            let countdownElement = countdownContainer.querySelector('[id^="countdown-"]');
            if (!countdownElement) {
                // إنشاء عنصر العداد إذا لم يكن موجوداً
                countdownElement = document.createElement('div');
                countdownElement.id = `countdown-${reservationId}`;
                countdownElement.className = 'countdown-timer ms-2';
                countdownElement.setAttribute('data-reservation-id', reservationId);
                
                // توقيت افتراضي - 24 ساعة من الآن
                const now = new Date();
                const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
                countdownElement.setAttribute('data-expire-time', tomorrow.toISOString());
                
                countdownElement.innerHTML = '<span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';
                
                // إضافة عنصر العداد إلى الحاوية
                countdownContainer.appendChild(countdownElement);
                
                console.log("تم إنشاء عداد جديد للحجز #" + reservationId);
            } else {
                // التأكد من أن العداد مرئي
                countdownElement.style.display = 'inline-block';
                countdownElement.style.visibility = 'visible';
                countdownElement.style.opacity = '1';
                console.log("تم تحديث العداد الموجود للحجز #" + reservationId);
            }
        });
    } else {
        console.log("لم يتم العثور على أي تحذير دفع، سيتم محاولة إنشاءها");
        
        // البحث عن حاويات محتملة للعداد
        const pendingPaymentRows = document.querySelectorAll('tr:has(.status-badge.status-confirmed):has(.payment-badge.payment-pending)');
        
        pendingPaymentRows.forEach(function(row) {
            // البحث عن خلية الإجراءات
            const actionsCell = row.querySelector('td:last-child');
            if (!actionsCell) return;
            
            // البحث عن معرف الحجز
            const idElement = row.querySelector('.reservation-id');
            let reservationId = "unknown";
            if (idElement) {
                reservationId = idElement.textContent.trim().replace('#', '');
            }
            
            // إنشاء عنصر تحذير الدفع إذا لم يكن موجوداً
            let paymentWarning = actionsCell.querySelector('.payment-warning');
            if (!paymentWarning) {
                paymentWarning = document.createElement('div');
                paymentWarning.className = 'payment-warning mt-2';
                paymentWarning.style.display = 'block';
                paymentWarning.style.visibility = 'visible';
                paymentWarning.style.opacity = '1';
                paymentWarning.style.width = '100%';
                
                const alertHtml = `
                    <div class="alert alert-danger py-2 px-3 mb-0" style="display: block !important; visibility: visible !important; opacity: 1 !important;">
                        <div class="countdown-container d-flex align-items-center justify-content-between">
                            <div>
                                <i class="fas fa-exclamation-triangle ms-1"></i>
                                <strong>مدة الدفع:</strong>
                            </div>
                            <div id="countdown-${reservationId}" class="countdown-timer ms-2" 
                                style="display: inline-block !important; visibility: visible !important; opacity: 1 !important; z-index: 999; position: relative;" 
                                data-reservation-id="${reservationId}">
                                <span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>
                            </div>
                        </div>
                    </div>
                `;
                
                paymentWarning.innerHTML = alertHtml;
                actionsCell.appendChild(paymentWarning);
                
                console.log("تم إنشاء تحذير دفع جديد للحجز #" + reservationId);
            }
        });
    }
}

/**
 * تحديث جميع العدادات التنازلية في الصفحة
 */
function updateAllCountdowns() {
    // البحث عن جميع عناصر العداد التنازلي في الصفحة
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
    // التأكد من أن العداد مرئي
    countdownElement.style.display = 'inline-block';
    countdownElement.style.visibility = 'visible';
    countdownElement.style.opacity = '1';
    
    // الحصول على وقت انتهاء الصلاحية
    let expireTimeStr = countdownElement.getAttribute('data-expire-time');
    
    // إذا لم يكن هناك وقت انتهاء، استخدم 24 ساعة من الآن
    if (!expireTimeStr) {
        const now = new Date();
        const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        expireTimeStr = tomorrow.toISOString();
        countdownElement.setAttribute('data-expire-time', expireTimeStr);
    }

    const expireTime = new Date(expireTimeStr);
    const now = new Date();
    
    // حساب الوقت المتبقي
    let remainingTime = expireTime - now;
    
    // البحث عن عناصر العرض
    const hoursElement = countdownElement.querySelector('.hours');
    const minutesElement = countdownElement.querySelector('.minutes');
    const secondsElement = countdownElement.querySelector('.seconds');
    
    // التأكد من وجود عناصر العرض
    if (!hoursElement || !minutesElement || !secondsElement) {
        console.log("لم يتم العثور على عناصر العداد في: " + countdownElement.id);
        // إعادة إنشاء عناصر العداد
        countdownElement.innerHTML = '<span class="hours">00</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';
        return;
    }
    
    // إذا انتهى الوقت
    if (remainingTime <= 0) {
        hoursElement.textContent = '00';
        minutesElement.textContent = '00';
        secondsElement.textContent = '00';
        
        // تغيير شكل العداد
        countdownElement.classList.remove('text-warning');
        countdownElement.classList.add('text-danger');
        
        // تحديث عنصر التنبيه
        const alertElement = countdownElement.closest('.alert');
        if (alertElement) {
            alertElement.classList.add('expired-alert');
        }
        
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
        countdownElement.classList.add('text-warning');
    }
    if (hours === 0 && minutes < 30) {
        countdownElement.classList.remove('text-warning');
        countdownElement.classList.add('text-danger');
    }
    
    // تحديث العداد
    hoursElement.textContent = hours.toString().padStart(2, '0');
    minutesElement.textContent = minutes.toString().padStart(2, '0');
    secondsElement.textContent = seconds.toString().padStart(2, '0');
}
