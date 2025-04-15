
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");

    // تحديد جميع عناصر الحجز التي تحتاج لعداد تنازلي
    const reservationItems = document.querySelectorAll('.reservation-item');
    console.log("تم العثور على " + reservationItems.length + " حجز");

    reservationItems.forEach(function(item) {
        // التحقق من وجود سمة تاريخ انتهاء الصلاحية
        const expiryDateAttr = item.getAttribute('data-expiry');
        console.log("سمة تاريخ الانتهاء: ", expiryDateAttr);

        // التحقق من وجود عنصر الحالة
        const statusElement = item.querySelector('.reservation-status');
        if (statusElement) {
            console.log("نص حالة الحجز: ", statusElement.textContent);
        }
        
        // التحقق من أن الحجز مؤكد من خلال فحص عنصر الحالة أو البحث عن الـ class
        // البحث عن النص "Confirmed" أو "تم التأكيد" لدعم اللغتين أو وجود class status-confirmed
        if (statusElement && 
            ((statusElement.textContent.trim().includes('Confirmed') || 
              statusElement.textContent.trim().includes('تم التأكيد') || 
              statusElement.querySelector('.status-confirmed')) && 
             expiryDateAttr && expiryDateAttr.trim() !== '')) {
            console.log("تم العثور على حجز مؤكد مع تاريخ انتهاء: ", expiryDateAttr);
            
            // إنشاء عنصر العداد التنازلي إذا لم يكن موجودًا
            let countdownElement = item.querySelector('.countdown-container');
            if (!countdownElement) {
                countdownElement = document.createElement('div');
                countdownElement.className = 'countdown-container';
                const dateCell = item.querySelector('.date-cell');
                if (dateCell) {
                    dateCell.appendChild(countdownElement);
                    console.log("تم إضافة عنصر العداد التنازلي");
                } else {
                    console.log("لم يتم العثور على عنصر الخلية التي تحتوي على التاريخ");
                }
            }

            // تحويل تاريخ الانتهاء إلى كائن Date
            try {
                const expiryDate = new Date(expiryDateAttr);
                console.log("تاريخ الانتهاء: ", expiryDate);
                
                if (!isNaN(expiryDate.getTime())) {
                    // تحديث العداد التنازلي كل ثانية
                    updateCountdown(countdownElement, expiryDate);
                    const interval = setInterval(function() {
                        updateCountdown(countdownElement, expiryDate);
                    }, 1000);
                    
                    // حفظ معرف الفاصل الزمني في العنصر لتنظيفه لاحقًا
                    item.setAttribute('data-interval-id', interval);
                    console.log("تم بدء العداد التنازلي");
                } else {
                    console.log("تاريخ الانتهاء غير صالح");
                }
            } catch (error) {
                console.error("خطأ في تحويل تاريخ الانتهاء: ", error);
            }
        }
    });

    // تحديث نص العداد التنازلي
    function updateCountdown(element, endTime) {
        const now = new Date();
        const remainingTime = endTime - now;

        // تحديد اللغة الحالية من عدة مصادر
        let currentLanguage = document.documentElement.lang || 'ar';
        
        // محاولة تحديد اللغة من خلال وجود العناصر أو الأنماط في الصفحة
        if (currentLanguage !== 'en' && currentLanguage !== 'ar') {
            // التحقق من وجود سمة dir="rtl" في عنصر html
            if (document.documentElement.getAttribute('dir') === 'rtl') {
                currentLanguage = 'ar';
            }
            // التحقق من اتجاه النص في عنصر body
            else if (window.getComputedStyle(document.body).direction === 'rtl') {
                currentLanguage = 'ar';
            }
            // محاولة تحديد اللغة من خلال البحث عن عناصر معينة في الصفحة
            else if (document.querySelector('html[lang="en"]')) {
                currentLanguage = 'en';
            }
            else if (document.querySelector('html[lang="ar"]')) {
                currentLanguage = 'ar';
            }
            // الافتراضي هو العربية
            else {
                currentLanguage = 'ar';
            }
        }
        
        const isEnglish = currentLanguage === 'en';
        console.log('اللغة الحالية:', currentLanguage, 'isEnglish:', isEnglish);

        if (remainingTime <= 0) {
            const expiredText = isEnglish ? 'Payment time expired' : 'انتهى وقت الدفع';
            element.innerHTML = `<div class="alert alert-danger p-2 mb-0"><small>${expiredText}</small></div>`;
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
            countdownText += isEnglish ? `${days} day${days > 1 ? 's' : ''} ` : `${days} يوم `;
        }
        countdownText += `${padZero(hours)}:${padZero(minutes)}:${padZero(seconds)}`;

        // تنسيق لون النص بناءً على الوقت المتبقي
        let colorClass = 'text-success';
        if (remainingTime < 3600000) { // أقل من ساعة
            colorClass = 'text-danger';
        } else if (remainingTime < 86400000) { // أقل من يوم
            colorClass = 'text-warning';
        }

        const remainingText = isEnglish ? 'Remaining payment time: ' : 'وقت الدفع المتبقي: ';
        
        // الحصول على معرف الحجز من أقرب رابط في عنصر الحجز
        const reservationRow = element.closest('.reservation-item');
        let reservationId = '';
        if (reservationRow) {
            const idCell = reservationRow.querySelector('a[href*="reservation_detail"]');
            if (idCell && idCell.textContent) {
                reservationId = idCell.textContent.trim().replace('#', '');
            }
        }
        
        // إنشاء زر الدفع السريع
        const payButton = reservationId ? 
            `<div class="mt-2">
                <a href="/checkout/${reservationId}" class="btn btn-sm btn-${colorClass.replace('text-', '')}">
                    <i class="fas fa-credit-card me-1"></i> ${isEnglish ? 'Pay Now' : 'ادفع الآن'}
                </a>
             </div>` : '';
        
        element.innerHTML = `
            <div class="mt-2 text-center p-2 border border-${colorClass.replace('text-', '')} rounded">
                <i class="fas fa-clock ${colorClass} me-1"></i>
                <span class="${colorClass} fw-bold">${remainingText}${countdownText}</span>
                ${payButton}
            </div>
        `;
    }

    function padZero(num) {
        return num.toString().padStart(2, '0');
    }
});
