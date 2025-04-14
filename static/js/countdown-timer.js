document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");

    // تحديد جميع عناصر الحجز التي تحتاج لعداد تنازلي
    const reservations = document.querySelectorAll('.reservation-item[data-expiry]');
    console.log("تم العثور على " + reservations.length + " عداد تنازلي");

    if (reservations.length === 0) {
        console.log("لم يتم العثور على أي عداد تنازلي، سيتم محاولة إنشاءها");

        // محاولة العثور على عناصر الحجز التي قد تكون موجودة بتنسيق مختلف
        const alternativeReservations = document.querySelectorAll('[data-expiry]');

        if (alternativeReservations.length > 0) {
            alternativeReservations.forEach(function(reservation) {
                initCountdown(reservation);
            });
        } else {
            // البحث عن عناصر تحتوي على تواريخ انتهاء في الصفحة
            const rows = document.querySelectorAll('.reservation-row, tr');
            rows.forEach(function(row) {
                const statusElement = row.querySelector('.reservation-status, .status-cell');
                if (statusElement && statusElement.textContent.includes('انتظار')) {
                    const dateElements = row.querySelectorAll('.date-cell, .expiry-date');
                    dateElements.forEach(function(dateEl) {
                        if (dateEl.textContent && !isNaN(new Date(dateEl.textContent).getTime())) {
                            const expiryDate = new Date(dateEl.textContent);
                            // إضافة عنصر العداد التنازلي
                            const countdownEl = document.createElement('div');
                            countdownEl.className = 'countdown-timer';
                            countdownEl.setAttribute('data-expiry', expiryDate.toISOString());
                            dateEl.appendChild(countdownEl);
                            initCountdown(countdownEl);
                        }
                    });
                }
            });
        }
    } else {
        // تهيئة العدادات التنازلية لجميع الحجوزات
        reservations.forEach(function(reservation) {
            initCountdown(reservation);
        });
    }

    // تهيئة عداد تنازلي محدد
    function initCountdown(element) {
        const expiryDateStr = element.getAttribute('data-expiry');
        if (!expiryDateStr) {
            return;
        }

        const expiryDate = new Date(expiryDateStr);
        if (isNaN(expiryDate.getTime())) {
            return;
        }

        // إنشاء أو الحصول على عنصر العداد التنازلي
        let countdownElement = element.querySelector('.countdown-timer');
        if (!countdownElement) {
            countdownElement = document.createElement('div');
            countdownElement.className = 'countdown-timer text-center mt-2 fw-bold';
            element.appendChild(countdownElement);
        }

        // تحديث العداد كل ثانية
        updateCountdown();
        const interval = setInterval(updateCountdown, 1000);

        function updateCountdown() {
            const now = new Date();
            const remainingTime = expiryDate - now;

            if (remainingTime <= 0) {
                clearInterval(interval);
                countdownElement.innerHTML = '<span class="text-danger">انتهى الوقت</span>';
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

            countdownElement.innerHTML = `<span class="${colorClass}">وقت الدفع المتبقي: ${countdownText}</span>`;
        }

        function padZero(num) {
            return num.toString().padStart(2, '0');
        }
    }
});