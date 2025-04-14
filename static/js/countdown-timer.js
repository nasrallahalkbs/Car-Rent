
// كود العداد التنازلي
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");
    
    // تحديد جميع عناصر العداد التنازلي
    const countdownTimers = document.querySelectorAll('.countdown-timer');
    
    // سجل عدد المؤقتات التي تم العثور عليها
    console.log("تم العثور على " + countdownTimers.length + " عداد تنازلي");
    
    // التحقق من خصائص البيانات لكل عنصر
    countdownTimers.forEach((timer, index) => {
        const expireTime = timer.getAttribute('data-expire-time');
        const reservationId = timer.getAttribute('data-reservation-id');
        console.log(`العداد ${index+1}: تاريخ الانتهاء = ${expireTime}, معرف الحجز = ${reservationId}`);
    });
    
    // إذا لم يتم العثور على أي عداد تنازلي، فحاول إنشاؤها استنادًا إلى البيانات المتاحة
    if (countdownTimers.length === 0) {
        console.log("لم يتم العثور على أي عداد تنازلي، سيتم محاولة إنشاءها");
        
        // البحث عن عناصر التنبيه التي قد تحتوي على معلومات المهلة
        const paymentWarnings = document.querySelectorAll('.payment-warning .alert');
        
        paymentWarnings.forEach(warning => {
            // التحقق من وجود بيانات المهلة
            const warningText = warning.textContent.trim();
            
            // إضافة عنصر العداد إذا لم يكن موجودًا
            if (!warning.querySelector('.countdown-timer')) {
                const timerDiv = document.createElement('div');
                timerDiv.className = 'countdown-timer ms-2';
                
                // محاولة استخراج معرف الحجز من السياق
                const reservationIdElement = warning.closest('tr')?.querySelector('.reservation-id');
                const reservationId = reservationIdElement ? reservationIdElement.textContent.replace('#', '') : '0';
                
                // إنشاء تاريخ انتهاء افتراضي (24 ساعة من الآن)
                const now = new Date();
                const expireTime = new Date(now.getTime() + 24 * 60 * 60 * 1000);
                
                timerDiv.setAttribute('data-expire-time', expireTime.toISOString());
                timerDiv.setAttribute('data-reservation-id', reservationId);
                timerDiv.innerHTML = '<span class="hours">24</span>:<span class="minutes">00</span>:<span class="seconds">00</span>';
                
                // إضافة العداد إلى التنبيه
                const textContainer = warning.querySelector('div > div:first-child');
                if (textContainer && textContainer.nextElementSibling) {
                    textContainer.parentNode.insertBefore(timerDiv, textContainer.nextElementSibling);
                } else {
                    warning.appendChild(timerDiv);
                }
                
                console.log("تم إنشاء عداد تنازلي جديد");
            }
        });
    }
    
    function updateCountdown() {
        // تحديد العناصر مرة أخرى في حالة إضافة عناصر جديدة
        const activeTimers = document.querySelectorAll('.countdown-timer');
        const now = new Date().getTime();
        
        activeTimers.forEach(timer => {
            try {
                // الحصول على وقت انتهاء المهلة
                const expireTimeStr = timer.getAttribute('data-expire-time');
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
                            const isEnglish = document.documentElement.lang === 'en';
                            textElement.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i> ' + 
                                (isEnglish ? 'Payment deadline expired!' : 'انتهت مهلة الدفع!');
                        }
                    }
                }
            } catch (e) {
                console.error('خطأ في تحديث العداد التنازلي:', e);
            }
        });
    }
    
    // تحديث العداد كل ثانية
    updateCountdown(); // تحديث فوري
    setInterval(updateCountdown, 1000); // تحديث كل ثانية
});
