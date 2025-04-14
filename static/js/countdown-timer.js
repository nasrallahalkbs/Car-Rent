
// كود العداد التنازلي
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");
    
    function initializeCountdownTimers() {
        // تحديد جميع عناصر العداد التنازلي
        const countdownTimers = document.querySelectorAll('.countdown-timer');
        console.log("تم العثور على " + countdownTimers.length + " عداد تنازلي");
        
        // إذا لم يتم العثور على أي عداد تنازلي، فحاول إنشاءها
        if (countdownTimers.length === 0) {
            console.log("لم يتم العثور على أي عداد تنازلي، سيتم إنشاؤها");
            createCountdownTimers();
        }
    }
    
    function createCountdownTimers() {
        // البحث عن جميع الحجوزات التي تحتاج عداداً تنازلياً
        const pendingPaymentRows = document.querySelectorAll('tr, .action-buttons');
        
        pendingPaymentRows.forEach(row => {
            // البحث عن الحجوزات المؤكدة التي تنتظر الدفع
            const hasConfirmedBadge = row.querySelector('.status-confirmed, .status-badge.status-confirmed');
            const hasPendingPaymentBadge = row.querySelector('.payment-pending, .payment-badge.payment-pending');
            
            if (hasConfirmedBadge && hasPendingPaymentBadge) {
                console.log("وجدت حجزاً بحاجة إلى عداد تنازلي");
                
                // البحث عن عنصر التحذير أو إنشاؤه إذا لم يكن موجوداً
                let paymentWarning = row.querySelector('.payment-warning');
                
                if (!paymentWarning) {
                    // البحث عن مكان مناسب لإضافة التحذير (في خلية الإجراءات)
                    const actionsCell = row.querySelector('td:last-child, .action-buttons');
                    
                    if (actionsCell) {
                        paymentWarning = document.createElement('div');
                        paymentWarning.className = 'payment-warning mt-2';
                        
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-danger py-2 px-3 mb-0';
                        
                        const flexDiv = document.createElement('div');
                        flexDiv.className = 'd-flex align-items-center justify-content-between';
                        
                        const textDiv = document.createElement('div');
                        textDiv.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i><strong>الوقت المتبقي للدفع:</strong>';
                        
                        // إنشاء عنصر العداد
                        const timerDiv = document.createElement('div');
                        timerDiv.className = 'countdown-timer ms-2';
                        timerDiv.style.display = 'inline-block';
                        timerDiv.style.visibility = 'visible';
                        
                        // محاولة استخراج معرف الحجز
                        const reservationIdElement = row.querySelector('.reservation-id');
                        const reservationId = reservationIdElement ? reservationIdElement.textContent.replace('#', '') : '0';
                        
                        // إنشاء تاريخ انتهاء افتراضي (24 ساعة من الآن)
                        const now = new Date();
                        const expireTime = new Date(now.getTime() + 24 * 60 * 60 * 1000);
                        
                        timerDiv.setAttribute('data-expire-time', expireTime.toISOString());
                        timerDiv.setAttribute('data-reservation-id', reservationId);
                        timerDiv.innerHTML = '<span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';
                        
                        // إضافة العناصر
                        flexDiv.appendChild(textDiv);
                        flexDiv.appendChild(timerDiv);
                        alertDiv.appendChild(flexDiv);
                        paymentWarning.appendChild(alertDiv);
                        actionsCell.appendChild(paymentWarning);
                        
                        console.log("تم إنشاء عداد تنازلي جديد");
                    }
                } else {
                    // تأكد من وجود عداد في عنصر التحذير
                    if (!paymentWarning.querySelector('.countdown-timer')) {
                        const alertDiv = paymentWarning.querySelector('.alert');
                        if (alertDiv) {
                            const flexDiv = alertDiv.querySelector('div') || alertDiv;
                            
                            const timerDiv = document.createElement('div');
                            timerDiv.className = 'countdown-timer ms-2';
                            timerDiv.style.display = 'inline-block';
                            timerDiv.style.visibility = 'visible';
                            
                            // محاولة استخراج معرف الحجز
                            const reservationIdElement = row.querySelector('.reservation-id');
                            const reservationId = reservationIdElement ? reservationIdElement.textContent.replace('#', '') : '0';
                            
                            // إنشاء تاريخ انتهاء افتراضي (24 ساعة من الآن)
                            const now = new Date();
                            const expireTime = new Date(now.getTime() + 24 * 60 * 60 * 1000);
                            
                            timerDiv.setAttribute('data-expire-time', expireTime.toISOString());
                            timerDiv.setAttribute('data-reservation-id', reservationId);
                            timerDiv.innerHTML = '<span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';
                            
                            flexDiv.appendChild(timerDiv);
                            console.log("تم إضافة عداد تنازلي إلى تحذير موجود");
                        }
                    }
                }
            }
        });
    }
    
    function updateCountdown() {
        // تحديد العناصر مرة أخرى في حالة إضافة عناصر جديدة
        const activeTimers = document.querySelectorAll('.countdown-timer');
        const now = new Date().getTime();
        
        if (activeTimers.length === 0) {
            console.log("لم يتم العثور على أي عداد تنازلي للعرض");
            // إعادة محاولة إنشاء العدادات
            createCountdownTimers();
            return;
        }
        
        activeTimers.forEach(timer => {
            try {
                // التأكد من أن العداد مرئي
                timer.style.display = 'inline-block';
                timer.style.visibility = 'visible';
                timer.style.opacity = '1';
                
                // الحصول على وقت انتهاء المهلة
                let expireTimeStr = timer.getAttribute('data-expire-time');
                if (!expireTimeStr) {
                    // إذا لم يكن هناك وقت انتهاء، استخدم 24 ساعة من الآن
                    const expireTime = new Date(now + 24 * 60 * 60 * 1000);
                    expireTimeStr = expireTime.toISOString();
                    timer.setAttribute('data-expire-time', expireTimeStr);
                }
                
                const expireTime = new Date(expireTimeStr).getTime();
                
                // تحديد عناصر الساعات والدقائق والثواني
                let hoursElement = timer.querySelector('.hours');
                let minutesElement = timer.querySelector('.minutes');
                let secondsElement = timer.querySelector('.seconds');
                
                // إذا لم تكن العناصر موجودة، قم بإنشائها
                if (!hoursElement || !minutesElement || !secondsElement) {
                    timer.innerHTML = `
                        <span class="hours">00</span>:<span class="minutes">00</span>:<span class="seconds">00</span>
                    `;
                    hoursElement = timer.querySelector('.hours');
                    minutesElement = timer.querySelector('.minutes');
                    secondsElement = timer.querySelector('.seconds');
                }
                
                // التأكد من أن العناصر موجودة الآن
                if (!hoursElement || !minutesElement || !secondsElement) {
                    console.error("فشل إنشاء عناصر العداد التنازلي");
                    return;
                }
                
                const timeLeft = expireTime - now;
                
                if (timeLeft > 0) {
                    // حساب الساعات والدقائق والثواني المتبقية
                    const hours = Math.floor(timeLeft / (1000 * 60 * 60));
                    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
                    
                    // تحديث العناصر في واجهة المستخدم
                    hoursElement.textContent = hours.toString().padStart(2, '0');
                    minutesElement.textContent = minutes.toString().padStart(2, '0');
                    secondsElement.textContent = seconds.toString().padStart(2, '0');
                    
                    // تغيير لون العداد حسب الوقت المتبقي
                    timer.classList.remove('d-none'); // التأكد من أن العداد مرئي
                    
                    if (timeLeft < 1000 * 60 * 60) { // أقل من ساعة
                        timer.classList.add('text-danger');
                        timer.classList.remove('text-warning');
                    } else if (timeLeft < 1000 * 60 * 60 * 3) { // أقل من 3 ساعات
                        timer.classList.add('text-warning');
                        timer.classList.remove('text-danger');
                    } else {
                        timer.classList.remove('text-warning');
                        timer.classList.remove('text-danger');
                    }
                } else {
                    // انتهت المهلة
                    hoursElement.textContent = '00';
                    minutesElement.textContent = '00';
                    secondsElement.textContent = '00';
                    timer.classList.add('text-danger');
                    timer.classList.remove('text-warning');
                    
                    // إضافة نص "انتهت المهلة"
                    const parentAlert = timer.closest('.alert');
                    if (parentAlert && !parentAlert.classList.contains('expired-alert')) {
                        parentAlert.classList.add('expired-alert', 'bg-danger', 'text-white');
                        const textElement = parentAlert.querySelector('div > div:first-child');
                        if (textElement) {
                            textElement.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i> انتهت مهلة الدفع!';
                        }
                    }
                }
            } catch (e) {
                console.error('خطأ في تحديث العداد التنازلي:', e);
            }
        });
    }
    
    // بدء تشغيل العدادات
    initializeCountdownTimers();
    
    // تحديث العداد كل ثانية
    updateCountdown(); // تحديث فوري
    setInterval(updateCountdown, 1000); // تحديث كل ثانية
    
    // إعادة تهيئة العدادات بعد 500 مللي ثانية (للتأكد من أن الصفحة تم تحميلها بالكامل)
    setTimeout(initializeCountdownTimers, 500);
});
