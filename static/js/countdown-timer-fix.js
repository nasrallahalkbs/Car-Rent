document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل مكون العد التنازلي المحدث");

    // الحصول على الوقت الحالي
    const now = new Date();
    
    // تحديد جميع الحجوزات في الصفحة - اختبار العديد من المحددات للتأكد من العمل في أي قالب
    let reservationItems = document.querySelectorAll('.reservation-item');
    
    if (reservationItems.length === 0) {
        // محاولة استهداف عناصر أخرى محتملة
        reservationItems = document.querySelectorAll('tr[id^="reservation-"]');
    }
    
    if (reservationItems.length === 0) {
        // محاولة استهداف أي صف في جدول الحجوزات
        const tables = document.querySelectorAll('table');
        tables.forEach(function(table) {
            if (table.querySelector('th') && 
                (table.querySelector('th').textContent.includes('RESERVATION ID') || 
                 table.querySelector('th').textContent.includes('حجز') || 
                 table.querySelector('th').textContent.includes('CAR'))) {
                const rows = table.querySelectorAll('tbody tr');
                reservationItems = rows;
            }
        });
    }
    
    console.log("تم العثور على " + reservationItems.length + " حجز");
    
    // معالجة كل حجز
    reservationItems.forEach(function(item, index) {
        console.log("معالجة الحجز رقم " + (index + 1));
        
        // البحث عن حالة الحجز وتاريخ انتهاء الصلاحية
        let statusElement = item.querySelector('.status-badge, .reservation-status, .status');
        let statusText = statusElement ? statusElement.textContent.trim() : '';
        
        // البحث عن زر الدفع كدليل على حجز في انتظار الدفع
        const hasPendingPayment = item.querySelector('a[href*="checkout"], a[href*="payment"], .btn-success');
        
        if (!statusText && statusElement) {
            const statusBadge = statusElement.querySelector('.status-badge, .badge');
            statusText = statusBadge ? statusBadge.textContent.trim() : '';
        }
        
        console.log("نص حالة الحجز: " + statusText);
        console.log("هل يحتاج للدفع: " + (hasPendingPayment ? "نعم" : "لا"));
        
        // التحقق من وجود تاريخ انتهاء الصلاحية
        let expiryDateAttr = item.getAttribute('data-expiry');
        let expiryDate = null;
        
        // إذا لم يكن هناك سمة تاريخ انتهاء، نحاول إنشاء تاريخ انتهاء تقديري (للاختبار)
        if (!expiryDateAttr && (statusText.includes('تم التأكيد') || statusText.includes('Confirmed') || hasPendingPayment)) {
            expiryDate = new Date(now);
            expiryDate.setHours(expiryDate.getHours() + 12);
            console.log("تم إنشاء تاريخ انتهاء تقديري: " + expiryDate);
        } else if (expiryDateAttr) {
            expiryDate = new Date(expiryDateAttr);
            console.log("تم قراءة تاريخ انتهاء: " + expiryDate);
        }
        
        // التحقق من أن الحجز مؤكد ويحتاج للدفع
        if ((statusText.includes('تم التأكيد') || statusText.includes('Confirmed') || hasPendingPayment) && expiryDate) {
            console.log("هذا الحجز مؤهل للعد التنازلي");
            
            // البحث عن الخلية المناسبة لإضافة العد التنازلي
            let dateCell = item.querySelector('.date-cell, td:nth-child(3)');
            
            if (!dateCell) {
                // محاولة البحث عن خلية التاريخ بطريقة أخرى
                const cells = item.querySelectorAll('td');
                cells.forEach(function(cell) {
                    if (cell.textContent.includes('/20') || cell.textContent.includes('-20')) {
                        dateCell = cell;
                    }
                });
            }
            
            if (!dateCell) {
                // إذا لم نجد خلية مناسبة، نستخدم الخلية الرابعة (التي تكون عادة للمدة أو الإجمالي)
                dateCell = item.querySelector('td:nth-child(4)');
            }
            
            if (dateCell) {
                console.log("تم العثور على خلية مناسبة للعد التنازلي");
                
                // التحقق من وجود عنصر العد التنازلي
                let countdownContainer = dateCell.querySelector('.countdown-container');
                
                if (!countdownContainer) {
                    console.log("إنشاء عنصر العد التنازلي");
                    countdownContainer = document.createElement('div');
                    countdownContainer.className = 'countdown-container mt-2';
                    dateCell.appendChild(countdownContainer);
                }
                
                // تحديث العد التنازلي
                function updateCountdown() {
                    const now = new Date();
                    const remainingTime = expiryDate - now;
                    
                    // تحديد اللغة
                    const isEnglish = document.documentElement.lang === 'en' || 
                                      statusText.includes('Confirmed') || 
                                      !statusText.includes('تم التأكيد');
                    
                    if (remainingTime <= 0) {
                        const expiredText = isEnglish ? 'Payment time expired' : 'انتهى وقت الدفع';
                        countdownContainer.innerHTML = `<div class="alert alert-danger p-2 mb-0"><small>${expiredText}</small></div>`;
                        return;
                    }
                    
                    // حساب الوقت المتبقي
                    const days = Math.floor(remainingTime / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((remainingTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
                    const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);
                    
                    // تنسيق نص العد التنازلي
                    let countdownText = '';
                    if (days > 0) {
                        countdownText += isEnglish ? `${days} day${days > 1 ? 's' : ''} ` : `${days} يوم `;
                    }
                    const padZero = (num) => num.toString().padStart(2, '0');
                    countdownText += `${padZero(hours)}:${padZero(minutes)}:${padZero(seconds)}`;
                    
                    // تنسيق لون النص بناءً على الوقت المتبقي
                    let colorClass = 'text-success';
                    if (remainingTime < 3600000) { // أقل من ساعة
                        colorClass = 'text-danger';
                    } else if (remainingTime < 86400000) { // أقل من يوم
                        colorClass = 'text-warning';
                    }
                    
                    const remainingText = isEnglish ? 'Remaining payment time: ' : 'وقت الدفع المتبقي: ';
                    const borderColor = colorClass.replace('text-', '');
                    
                    countdownContainer.innerHTML = `
                        <div class="p-2 border border-${borderColor} rounded text-center">
                            <div class="${colorClass} fw-bold">
                                <i class="fas fa-clock me-1"></i>
                                ${remainingText}${countdownText}
                            </div>
                            <a href="/checkout/${item.id || index + 1}" class="btn btn-sm btn-${borderColor} mt-1">
                                <i class="fas fa-credit-card me-1"></i>
                                ${isEnglish ? 'Pay Now' : 'ادفع الآن'}
                            </a>
                        </div>
                    `;
                }
                
                // التحديث الأولي
                updateCountdown();
                
                // تحديث العد التنازلي كل ثانية
                const timerId = setInterval(updateCountdown, 1000);
                console.log("تم بدء العد التنازلي بنجاح");
                
                // تخزين معرف المؤقت للتنظيف لاحقًا
                item.setAttribute('data-timer-id', timerId);
            } else {
                console.error("لم يتم العثور على خلية مناسبة لإضافة العد التنازلي");
            }
        } else {
            console.log("هذا الحجز غير مؤهل للعد التنازلي أو انتهت صلاحيته");
        }
    });
});