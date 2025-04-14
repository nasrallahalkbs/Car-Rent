document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل صفحة العداد التنازلي');

    // البحث عن جميع الحجوزات التي تحتاج إلى عداد تنازلي
    const reservationRows = document.querySelectorAll('tr[data-expiry]');
    console.log(`تم العثور على ${reservationRows.length} حجز`);

    // إعداد العداد التنازلي لكل حجز
    reservationRows.forEach(function(row) {
        // التحقق من حالة الدفع قبل إنشاء العداد التنازلي
        const isPaid = checkIfReservationIsPaid(row);
        if (!isPaid) {
            initializeCountdown(row);
        }
    });

    // البحث عن عناصر العد التنازلي المستقلة
    const countdownContainers = document.querySelectorAll('.countdown-container[data-expiry]');

    // إعداد العداد التنازلي لكل عنصر مستقل
    countdownContainers.forEach(function(container) {
        // التحقق مما إذا كان الحجز مدفوعاً قبل إنشاء العداد التنازلي
        const row = container.closest('.reservation-item, tr');
        const isPaid = row ? checkIfReservationIsPaid(row) : false;

        if (!isPaid && !container.hasAttribute('data-initialized')) {
            const expiryDateStr = container.getAttribute('data-expiry');
            if (expiryDateStr) {
                const expiryDate = new Date(expiryDateStr);
                startCountdown(container, expiryDate);
                container.setAttribute('data-initialized', 'true');
            }
        } else if (isPaid) {
            // إذا كان الحجز مدفوعاً، نحذف العداد التنازلي
            container.remove();
        }
    });
});

/**
 * التحقق مما إذا كان الحجز مدفوعاً
 * @param {HTMLElement} row - صف الحجز
 * @returns {boolean} - يعود true إذا كان الحجز مدفوعاً، وإلا يعود false
 */
function checkIfReservationIsPaid(row) {
    // البحث عن عنصر الحالة
    const statusBadge = row.querySelector('.status-paid, .status-badge.status-paid');
    
    // التحقق من وجود بطاقة "مدفوع"
    if (statusBadge) {
        return true;
    }
    
    // البحث عن نص "مدفوع" في خلية الحالة
    const statusText = row.textContent || '';
    const hasPaidStatus = statusText.includes('مدفوع') || statusText.includes('Paid');
    
    // البحث عن زر "مدفوع" في صف الحجز
    const paidButton = row.querySelector('a:contains("مدفوع"), a:contains("Paid")');
    
    return hasPaidStatus || (paidButton !== null);
}

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
        // التحقق مما إذا كان العنصر ما زال موجوداً في DOM
        if (!document.contains(countdownElement)) {
            clearInterval(countdownInterval);
            return;
        }

        // الوقت الحالي
        const now = new Date().getTime();

        // حساب الفرق بين الوقت الحالي وتاريخ الانتهاء
        const timeRemaining = expiryDate.getTime() - now;

        // التحقق مما إذا كان الوقت قد انتهى
        if (timeRemaining <= 0) {
            // عرض رسالة انتهاء الصلاحية
            countdownElement.innerHTML = `
                <div class="alert alert-danger p-2 mb-0 text-center">
                    <i class="fas fa-exclamation-triangle ms-1"></i>
                    <small>انتهت مدة الدفع</small>
                </div>
            `;

            // إيقاف تحديث العد التنازلي
            clearInterval(countdownInterval);
            return;
        }

        // حساب الأيام والساعات والدقائق والثواني المتبقية
        const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

        // تحديد لون النص وفئة التنبيه بناءً على الوقت المتبقي
        let alertClass = 'alert-success';
        let textClass = 'text-success';

        if (timeRemaining < 3600000) { // أقل من ساعة
            alertClass = 'alert-danger';
            textClass = 'text-danger';
        } else if (timeRemaining < 86400000) { // أقل من يوم
            alertClass = 'alert-warning';
            textClass = 'text-warning';
        }

        // إنشاء نص العد التنازلي بتنسيق محسن
        let timeDisplay = '';
        if (days > 0) {
            timeDisplay += `<span class="fw-bold">${days}</span> يوم `;
        }
        
        timeDisplay += `<span class="fw-bold">${padZero(hours)}</span>:<span class="fw-bold">${padZero(minutes)}</span>:<span class="fw-bold">${padZero(seconds)}</span>`;

        // تحديث نص العد التنازلي بتصميم محسن
        countdownElement.innerHTML = `
            <div class="alert ${alertClass} p-2 mb-0 text-center">
                <i class="fas fa-clock me-1 ${textClass}"></i>
                <small>وقت الدفع المتبقي: ${timeDisplay}</small>
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

/**
 * إضافة أصفار للأرقام الأصغر من 10
 * @param {number} num - الرقم المراد تنسيقه
 * @returns {string} - الرقم مع إضافة صفر في البداية إذا كان أقل من 10
 */
function padZero(num) {
    return num.toString().padStart(2, '0');
}