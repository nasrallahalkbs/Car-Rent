
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");

    // تحديد جميع عناصر الحجز التي تحتاج لعداد تنازلي
    const reservationItems = document.querySelectorAll('.reservation-item');
    console.log("تم العثور على " + reservationItems.length + " حجز");

    reservationItems.forEach(function(item) {
        // التحقق من حالة الحجز عن طريق البحث عن عنصر الحالة
        const statusElement = item.querySelector('.reservation-status');
        
        if (statusElement && statusElement.textContent.includes('تم التأكيد')) {
            // الحصول على تاريخ انتهاء صلاحية تأكيد الحجز
            const expiryDateAttr = item.getAttribute('data-expiry');
            
            // التأكد من أن سمة تاريخ الانتهاء موجودة وليست فارغة
            if (expiryDateAttr && expiryDateAttr !== 'None' && expiryDateAttr !== '') {
                console.log("وجدت حجز مؤكد مع تاريخ انتهاء: " + expiryDateAttr);
                
                // إنشاء عنصر العداد التنازلي
                let countdownElement = item.querySelector('.countdown-container');
                if (!countdownElement) {
                    countdownElement = document.createElement('div');
                    countdownElement.className = 'countdown-container mt-2';
                    const dateCell = item.querySelector('.date-cell');
                    if (dateCell) {
                        dateCell.appendChild(countdownElement);
                    }
                }

                // تحويل تاريخ الانتهاء إلى كائن Date
                const expiryDate = new Date(expiryDateAttr);
                
                if (!isNaN(expiryDate.getTime())) {
                    // تحديث العداد التنازلي مباشرة
                    updateCountdown(countdownElement, expiryDate);
                    
                    // ثم تحديثه كل ثانية
                    const interval = setInterval(function() {
                        updateCountdown(countdownElement, expiryDate);
                    }, 1000);
                    
                    // حفظ معرف الفاصل الزمني للتنظيف لاحقاً
                    item.setAttribute('data-interval-id', interval);
                } else {
                    console.error("تاريخ انتهاء الصلاحية غير صالح: ", expiryDateAttr);
                }
            } else {
                console.log("حجز مؤكد بدون تاريخ انتهاء صلاحية");
            }
        }
    });

    // تحديث نص العداد التنازلي
    function updateCountdown(element, endTime) {
        const now = new Date();
        const remainingTime = endTime - now;

        if (remainingTime <= 0) {
            element.innerHTML = '<div class="alert alert-danger p-2 mb-0"><small>انتهى وقت الدفع</small></div>';
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

        element.innerHTML = `<div class="text-center"><span class="${colorClass} fw-bold">وقت الدفع المتبقي: ${countdownText}</span></div>`;
    }

    function padZero(num) {
        return num.toString().padStart(2, '0');
    }
});
