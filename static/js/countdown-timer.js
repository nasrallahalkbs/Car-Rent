document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");

    // تحديد جميع عناصر الحجز التي تحتاج لعداد تنازلي
    const reservationItems = document.querySelectorAll('.reservation-item');
    console.log("تم العثور على " + reservationItems.length + " حجز");

    reservationItems.forEach(function(item) {
        if (item.querySelector('.reservation-status') && 
            item.querySelector('.reservation-status').textContent.includes('انتظار')) {

            // إنشاء عنصر العداد التنازلي إذا لم يكن موجودًا
            let countdownElement = item.querySelector('.countdown-container');
            if (!countdownElement) {
                countdownElement = document.createElement('div');
                countdownElement.className = 'countdown-container';
                const dateCell = item.querySelector('.date-cell');
                if (dateCell) {
                    dateCell.appendChild(countdownElement);
                }
            }

            // الحصول على تاريخ الانتهاء (استخدام data-expiry إذا كان موجودًا، أو إنشاء تاريخ بعد 24 ساعة من الآن)
            const expiryDateAttr = item.getAttribute('data-expiry');
            let expiryDate;

            if (expiryDateAttr && expiryDateAttr !== 'None' && expiryDateAttr !== '') {
                expiryDate = new Date(expiryDateAttr);
            } else {
                // إذا لم يتم تحديد تاريخ انتهاء، استخدم 24 ساعة من الآن كوقت افتراضي
                expiryDate = new Date();
                expiryDate.setHours(expiryDate.getHours() + 24);
            }

            if (!isNaN(expiryDate.getTime())) {
                // تحديث العداد التنازلي كل ثانية
                updateCountdown(countdownElement, expiryDate);
                const interval = setInterval(function() {
                    updateCountdown(countdownElement, expiryDate);
                }, 1000);
            }
        }
    });

    // تحديث نص العداد التنازلي
    function updateCountdown(element, endTime) {
        const now = new Date();
        const remainingTime = endTime - now;

        if (remainingTime <= 0) {
            element.innerHTML = '<span class="text-danger fw-bold">انتهى وقت الدفع</span>';
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

        element.innerHTML = `<div class="mt-2 text-center"><span class="${colorClass} fw-bold">وقت الدفع المتبقي: ${countdownText}</span></div>`;
    }

    function padZero(num) {
        return num.toString().padStart(2, '0');
    }
});