
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");

    // تحديد جميع عناصر الحجز التي تحتاج لعداد تنازلي
    const reservationItems = document.querySelectorAll('.reservation-item');
    console.log("تم العثور على " + reservationItems.length + " حجز");

    reservationItems.forEach(function(item) {
        // تحقق ما إذا كان الحجز في حالة انتظار (معلق) وله تاريخ انتهاء
        if (item.getAttribute('data-expiry')) {
            // إنشاء عنصر العداد التنازلي
            let countdownContainer = item.querySelector('.countdown-container');
            if (!countdownContainer) {
                countdownContainer = document.createElement('div');
                countdownContainer.className = 'countdown-container mt-2';
                const dateCell = item.querySelector('.date-cell');
                if (dateCell) {
                    dateCell.appendChild(countdownContainer);
                }
            }

            // الحصول على تاريخ الانتهاء
            const expiryDateAttr = item.getAttribute('data-expiry');
            
            if (expiryDateAttr && expiryDateAttr !== 'None' && expiryDateAttr !== '') {
                const expiryDate = new Date(expiryDateAttr);
                
                if (!isNaN(expiryDate.getTime())) {
                    // تحديث العداد التنازلي فورًا
                    updateCountdown(countdownContainer, expiryDate);
                    
                    // تحديث العداد كل ثانية
                    const interval = setInterval(function() {
                        updateCountdown(countdownContainer, expiryDate);
                    }, 1000);
                    
                    // تخزين الفاصل الزمني في عنصر DOM ليتم تنظيفه لاحقًا إذا لزم الأمر
                    item.setAttribute('data-interval-id', interval);
                } else {
                    console.log("تاريخ انتهاء غير صالح: " + expiryDateAttr);
                }
            }
        }
    });

    // تحديث نص العداد التنازلي
    function updateCountdown(element, endTime) {
        const now = new Date();
        const remainingTime = endTime - now;

        if (remainingTime <= 0) {
            element.innerHTML = '<div class="alert alert-danger p-1 mb-0"><small>انتهى وقت الدفع</small></div>';
            return;
        }

        // حساب الوقت المتبقي
        const days = Math.floor(remainingTime / (1000 * 60 * 60 * 24));
        const hours = Math.floor((remainingTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);

        // تنسيق نص العداد التنازلي
        let countdownText = '';
        if (days > 0) {
            countdownText += `${days} يوم `;
        }
        countdownText += `${padZero(hours)}:${padZero(minutes)}:${padZero(seconds)}`;

        // تنسيق لون النص بناءً على الوقت المتبقي
        let colorClass = 'text-success';
        if (remainingTime < 3600000) { // أقل من ساعة
            colorClass = 'text-danger';
        } else if (remainingTime < 86400000) { // أقل من يوم
            colorClass = 'text-warning';
        }

        element.innerHTML = `<div class="countdown-timer ${colorClass} fw-bold small"><i class="fas fa-clock me-1"></i> وقت الدفع المتبقي: ${countdownText}</div>`;
    }

    function padZero(num) {
        return num.toString().padStart(2, '0');
    }
});
