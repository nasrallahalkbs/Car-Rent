document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل صفحة العداد التنازلي');

    // البحث عن جميع الحجوزات التي تحتاج إلى عداد تنازلي
    const reservationRows = document.querySelectorAll('tr[data-expiry]');
    console.log(`تم العثور على ${reservationRows.length} حجز`);

    // إعداد العداد التنازلي لكل حجز
    reservationRows.forEach(function(row) {
        initializeCountdown(row);
    });

    // البحث عن عناصر العد التنازلي المستقلة
    const countdownContainers = document.querySelectorAll('.countdown-container[data-expiry]');

    // إعداد العداد التنازلي لكل عنصر مستقل
    countdownContainers.forEach(function(container) {
        if (!container.hasAttribute('data-initialized')) {
            const expiryDateStr = container.getAttribute('data-expiry');
            if (expiryDateStr) {
                const expiryDate = new Date(expiryDateStr);
                startCountdown(container, expiryDate);
                container.setAttribute('data-initialized', 'true');
            }
        }
    });
});

/**
 * تهيئة العداد التنازلي لصف حجز معين
 * @param {HTMLElement} row - صف الحجز الذي يحتوي على بيانات تاريخ الانتهاء
 */
function initializeCountdown(row) {
    // الحصول على تاريخ انتهاء الصلاحية من سمات الصف
    const expiryDateStr = row.getAttribute('data-expiry');

    if (!expiryDateStr) {
        console.log('لا يوجد تاريخ انتهاء للحجز:', row.id);
        return;
    }

    // تحويل نص التاريخ إلى كائن تاريخ
    const expiryDate = new Date(expiryDateStr);

    // التحقق من صحة التاريخ
    if (isNaN(expiryDate.getTime())) {
        console.log('تاريخ انتهاء الصلاحية غير صالح:', expiryDateStr);
        return;
    }

    // البحث عن حاوية العداد التنازلي داخل الصف
    let countdownContainer = row.querySelector('.countdown-container');

    // إذا لم يكن هناك حاوية للعد التنازلي، نقوم بإنشائها
    if (!countdownContainer) {
        // البحث عن خلية الحالة
        const statusCell = row.querySelector('td:nth-child(6)');

        if (statusCell) {
            // إنشاء حاوية العد التنازلي
            countdownContainer = document.createElement('div');
            countdownContainer.className = 'countdown-container mt-2';
            countdownContainer.setAttribute('data-expiry', expiryDateStr);

            // إضافة حاوية العد التنازلي إلى خلية الحالة
            statusCell.appendChild(countdownContainer);
        } else {
            console.log('لم يتم العثور على خلية الحالة في:', row.id);
            return;
        }
    }

    // بدء العد التنازلي
    startCountdown(countdownContainer, expiryDate);
}

/**
 * بدء عملية العد التنازلي لعنصر معين
 * @param {HTMLElement} countdownElement - عنصر HTML الذي سيعرض العد التنازلي
 * @param {Date} expiryDate - تاريخ انتهاء الصلاحية
 */
function startCountdown(countdownElement, expiryDate) {
    // دالة لتحديث العد التنازلي
    function updateCountdown() {
        // الوقت الحالي
        const now = new Date().getTime();

        // حساب الفرق بين الوقت الحالي وتاريخ الانتهاء
        const timeRemaining = expiryDate.getTime() - now;

        // التحقق مما إذا كان الوقت قد انتهى
        if (timeRemaining <= 0) {
            // عرض رسالة انتهاء الصلاحية
            countdownElement.innerHTML = `
                <div class="countdown-expired">
                    <i class="fas fa-exclamation-triangle ms-1"></i>
                    انتهت مدة الدفع
                </div>
            `;

            // إيقاف تحديث العد التنازلي
            clearInterval(countdownInterval);
            return;
        }

        // حساب الساعات والدقائق والثواني المتبقية
        const hours = Math.floor(timeRemaining / (1000 * 60 * 60));
        const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

        // تحديد لون النص بناءً على الوقت المتبقي
        let colorClass = 'countdown-normal';

        if (hours < 2) {
            colorClass = 'countdown-warning';
        }

        if (hours < 1) {
            colorClass = 'countdown-expired';
        }

        // تحديث نص العد التنازلي
        countdownElement.innerHTML = `
            <div class="${colorClass}">
                <i class="fas fa-clock ms-1"></i>
                ينتهي الدفع خلال: ${hours} ساعة ${minutes} دقيقة ${seconds} ثانية
            </div>
        `;
    }

    // تحديث العد التنازلي للمرة الأولى
    updateCountdown();

    // تحديث العد التنازلي كل ثانية
    const countdownInterval = setInterval(updateCountdown, 1000);

    // تخزين معرف الفاصل الزمني في سمة العنصر للرجوع إليه لاحقًا
    countdownElement.setAttribute('data-interval-id', countdownInterval);
}