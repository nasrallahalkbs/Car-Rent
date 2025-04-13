// كود العداد التنازلي
document.addEventListener('DOMContentLoaded', function() {
    // تحديد جميع عناصر العداد التنازلي
    const countdownTimers = document.querySelectorAll('.countdown-timer');
    
    // سجل عدد المؤقتات التي تم العثور عليها
    console.log("تم العثور على " + countdownTimers.length + " عداد تنازلي");
    
    // التحقق من خصائص البيانات لكل عنصر
    countdownTimers.forEach((timer, index) => {
        const expireTime = timer.getAttribute('data-expire-time');
        const reservationId = timer.getAttribute('data-reservation-id');
        console.log(`العداد ${index+1}: تاريخ الانتهاء = ${expireTime}, معرف الحجز = ${reservationId}`);
        
        // التحقق من صحة تنسيق التاريخ
        try {
            const date = new Date(expireTime);
            console.log(`تاريخ منسق: ${date.toString()}`);
        } catch (e) {
            console.error(`خطأ في تنسيق التاريخ: ${e.message}`);
        }
    });
    
    function updateCountdown() {
        const now = new Date().getTime();
        
        countdownTimers.forEach(timer => {
            try {
                // الحصول على وقت انتهاء المهلة
                const expireTimeStr = timer.getAttribute('data-expire-time');
                const expireTime = new Date(expireTimeStr).getTime();
                
                // سجل معلومات تصحيح الوقت المتبقي للمرة الأولى فقط
                if (!timer.hasAttribute('data-debug-logged')) {
                    console.log(`تاريخ الانتهاء: ${expireTimeStr}`);
                    console.log(`الوقت الحالي: ${new Date(now).toISOString()}`);
                    console.log(`الوقت المتبقي بالمللي ثانية: ${expireTime - now}`);
                    timer.setAttribute('data-debug-logged', 'true');
                }
                
                const timeLeft = expireTime - now;
                
                // تحديد عناصر الساعات والدقائق والثواني
                const hoursElement = timer.querySelector('.hours');
                const minutesElement = timer.querySelector('.minutes');
                const secondsElement = timer.querySelector('.seconds');
                
                if (!hoursElement || !minutesElement || !secondsElement) {
                    console.error('لم يتم العثور على عناصر العرض (ساعات، دقائق، ثواني)');
                    return;
                }
                
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
                    if (timeLeft < 1000 * 60 * 60) { // أقل من ساعة
                        timer.classList.add('text-danger');
                        timer.classList.add('fw-bold');
                    } else if (timeLeft < 1000 * 60 * 60 * 3) { // أقل من 3 ساعات
                        timer.classList.add('text-warning');
                    }
                } else {
                    // انتهت المهلة
                    hoursElement.textContent = '00';
                    minutesElement.textContent = '00';
                    secondsElement.textContent = '00';
                    timer.classList.add('text-danger');
                    timer.classList.add('expired');
                    
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
    if (countdownTimers.length > 0) {
        updateCountdown(); // تحديث فوري
        setInterval(updateCountdown, 1000); // تحديث كل ثانية
    } else {
        console.log("لم يتم العثور على أي عداد تنازلي للعرض");
    }
});