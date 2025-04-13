// كود العداد التنازلي
document.addEventListener('DOMContentLoaded', function() {
    // تحديد جميع عناصر العداد التنازلي
    const countdownTimers = document.querySelectorAll('.countdown-timer');
    
    function updateCountdown() {
        const now = new Date().getTime();
        
        countdownTimers.forEach(timer => {
            // الحصول على وقت انتهاء المهلة
            const expireTime = new Date(timer.getAttribute('data-expire-time')).getTime();
            const timeLeft = expireTime - now;
            
            // تحديد عناصر الساعات والدقائق والثواني
            const hoursElement = timer.querySelector('.hours');
            const minutesElement = timer.querySelector('.minutes');
            const secondsElement = timer.querySelector('.seconds');
            
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
                    parentAlert.querySelector('div > div:first-child').innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i> انتهت مهلة الدفع!';
                }
            }
        });
    }
    
    // تحديث العداد كل ثانية
    if (countdownTimers.length > 0) {
        console.log("تم العثور على " + countdownTimers.length + " عداد تنازلي");
        updateCountdown(); // تحديث فوري
        setInterval(updateCountdown, 1000); // تحديث كل ثانية
    } else {
        console.log("لم يتم العثور على أي عداد تنازلي");
    }
});