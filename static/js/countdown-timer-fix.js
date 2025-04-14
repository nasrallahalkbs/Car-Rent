document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة العداد التنازلي");

    // الحصول على الوقت الحالي
    const now = new Date();
    
    // البحث عن حاويات العد التنازلي المضافة من HTML مباشرة
    const countdownContainers = document.querySelectorAll('.countdown-container[data-reservation-id]');
    if (countdownContainers.length > 0) {
        console.log("تم العثور على " + countdownContainers.length + " حاوية عد تنازلي جاهزة");
        
        countdownContainers.forEach(function(container) {
            const reservationId = container.getAttribute('data-reservation-id');
            console.log(`معالجة العد التنازلي للحجز رقم ${reservationId}`);
            
            // معالجة تاريخ الانتهاء
            let expiryDateAttr = container.getAttribute('data-expiry');
            let expiryDate = null;
            
            if (expiryDateAttr && expiryDateAttr !== "None") {
                try {
                    expiryDate = new Date(expiryDateAttr);
                    console.log(`تاريخ انتهاء الحجز ${reservationId}: ${expiryDate}`);
                } catch (e) {
                    console.error(`خطأ في تحويل تاريخ الانتهاء للحجز ${reservationId}: ${e}`);
                }
            }
            
            // إذا لم نجد تاريخ صالح، نستخدم تاريخ افتراضي (بعد 24 ساعة من الآن)
            if (!expiryDate || isNaN(expiryDate.getTime())) {
                expiryDate = new Date(now);
                expiryDate.setHours(expiryDate.getHours() + 24);
                console.log(`تم استخدام تاريخ افتراضي للحجز ${reservationId}: ${expiryDate}`);
            }
            
            // هل هي باللغة الإنجليزية أم العربية
            const isEnglish = document.documentElement.lang === 'en' || document.body.getAttribute('dir') !== 'rtl';
            
            // إضافة العد التنازلي لهذا العنصر
            function updateCountdown() {
                const now = new Date();
                const remainingTime = expiryDate - now;
                
                if (remainingTime <= 0) {
                    const expiredText = isEnglish ? 'Payment time expired' : 'انتهى وقت الدفع';
                    container.innerHTML = `<small class="text-danger">${expiredText}</small>`;
                    return;
                }
                
                // حساب الوقت المتبقي
                const hours = Math.floor(remainingTime / (1000 * 60 * 60));
                const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);
                
                // تنسيق النص
                const padZero = (num) => num.toString().padStart(2, '0');
                let countdownText = `${padZero(hours)}:${padZero(minutes)}:${padZero(seconds)}`;
                
                // تحديد اللون بناء على الوقت المتبقي
                let colorClass = 'text-success';
                if (remainingTime < 3600000) { // أقل من ساعة
                    colorClass = 'text-danger';
                } else if (remainingTime < 86400000) { // أقل من يوم
                    colorClass = 'text-warning';
                }
                
                container.innerHTML = `
                    <div class="${colorClass} fw-bold d-inline-block">
                        <i class="fas fa-clock me-1"></i>
                        ${countdownText}
                    </div>
                `;
            }
            
            // التحديث الأولي
            updateCountdown();
            
            // تحديث العد التنازلي كل ثانية
            const timerId = setInterval(updateCountdown, 1000);
            console.log(`تم بدء العد التنازلي للحجز ${reservationId}`);
            
            // تخزين معرف المؤقت للتنظيف لاحقًا
            container.setAttribute('data-timer-id', timerId);
        });
    }
    
    // تحديد جميع الحجوزات في الصفحة - اختبار العديد من المحددات للتأكد من العمل في أي قالب
    let reservationItems = document.querySelectorAll('.reservation-item');
    
    if (reservationItems.length === 0) {
        // محاولة استهداف عناصر أخرى محتملة
        reservationItems = document.querySelectorAll('tr[id^="reservation-"]');
    }
    
    if (reservationItems.length === 0) {
        // محاولة استهداف أي صف في جدول الحجوزات
        const tables = document.querySelectorAll('table');
        for (let i = 0; i < tables.length; i++) {
            const table = tables[i];
            console.log("فحص الجدول رقم " + (i+1));
            
            // طباعة جميع الرؤوس للتحقق
            const headers = table.querySelectorAll('th');
            if (headers.length > 0) {
                console.log("رؤوس الجدول:");
                headers.forEach(th => console.log(" - " + th.textContent.trim()));
                
                // تحقق من وجود عمود معرف الحجز
                if (Array.from(headers).some(th => 
                    th.textContent.includes('RESERVATION') || 
                    th.textContent.includes('حجز') || 
                    th.textContent.includes('رقم الحجز'))) {
                    
                    console.log("تم العثور على جدول الحجوزات");
                    reservationItems = table.querySelectorAll('tbody tr');
                    break;
                }
            }
        }
    }
    
    // محاولة أخيرة: استهداف أي صف في أي جدول إذا لم يتم العثور على شيء
    if (reservationItems.length === 0) {
        reservationItems = document.querySelectorAll('table tbody tr');
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
        
        // إظهار التفاصيل للتصحيح
        console.log("سمة data-expiry: " + expiryDateAttr);
        
        // بيانات للتصحيح: طباعة جميع السمات للعنصر
        console.log("جميع سمات العنصر:");
        for (let i = 0; i < item.attributes.length; i++) {
            const attr = item.attributes[i];
            console.log(`  ${attr.name}: ${attr.value}`);
        }
        
        // إذا لم يكن هناك سمة تاريخ انتهاء، نبحث عن أي نص تاريخ في العنصر
        if (!expiryDateAttr || expiryDateAttr === "None" || expiryDateAttr === "") {
            console.log("لا يوجد سمة data-expiry صالحة، البحث عن بدائل...");
            
            // خيار 1: البحث عن عنصر تاريخ الانتهاء في الخلية
            const dateCell = item.querySelector('.date-cell');
            if (dateCell) {
                const dateText = dateCell.textContent.trim();
                console.log("نص خلية التاريخ: " + dateText);
                
                // محاولة العثور على تاريخ مستقبلي (للاختبار فقط)
                const tomorrow = new Date(now);
                tomorrow.setDate(tomorrow.getDate() + 1);
                console.log("استخدام تاريخ مستقبلي للاختبار: " + tomorrow);
                expiryDate = tomorrow;
            } else {
                // خيار 2: إنشاء تاريخ انتهاء تقديري للاختبار
                if (statusText.includes('تم التأكيد') || statusText.includes('Confirmed') || hasPendingPayment) {
                    expiryDate = new Date(now);
                    expiryDate.setHours(expiryDate.getHours() + 12);
                    console.log("تم إنشاء تاريخ انتهاء تقديري: " + expiryDate);
                }
            }
        } else {
            // تحويل سمة التاريخ إلى كائن Date
            try {
                expiryDate = new Date(expiryDateAttr);
                console.log("تم قراءة تاريخ انتهاء: " + expiryDate);
            } catch (e) {
                console.error("خطأ في تحويل تاريخ الانتهاء: " + e);
                
                // خيار بديل للاختبار
                expiryDate = new Date(now);
                expiryDate.setHours(expiryDate.getHours() + 24);
                console.log("تم إنشاء تاريخ انتهاء بديل: " + expiryDate);
            }
        }
        
        // للاختبار فقط: إنشاء تاريخ انتهاء إذا لم يتم العثور على تاريخ صالح
        if (!expiryDate || isNaN(expiryDate.getTime())) {
            console.log("لم يتم العثور على تاريخ انتهاء صالح، إنشاء تاريخ للاختبار");
            expiryDate = new Date(now);
            expiryDate.setHours(expiryDate.getHours() + 24);
        }
        
        // التحقق من أن الحجز مؤكد ويحتاج للدفع
        if ((statusText.includes('تم التأكيد') || statusText.includes('Confirmed') || hasPendingPayment) && expiryDate) {
            console.log("هذا الحجز مؤهل للعد التنازلي");
            
            // البحث عن خلية الإجراءات (حيث توجد أزرار الدفع)
            const actionsCell = item.querySelector('td:last-child');

            if (!actionsCell) {
                console.error("لم يتم العثور على خلية الإجراءات");
                return;
            }

            // البحث عن أزرار الإجراءات
            const actionButtons = actionsCell.querySelector('.action-buttons');
            
            if (!actionButtons) {
                console.error("لم يتم العثور على حاوية أزرار الإجراءات");
                return;
            }
            
            // البحث عن زر الدفع
            const payButton = actionButtons.querySelector('.btn-pay');
            
            if (!payButton) {
                console.log("لم يتم العثور على زر الدفع");
                return;
            }
            
            console.log("تم العثور على زر الدفع، سيتم إضافة العد التنازلي بجانبه");

            // نستخدم حاوية أزرار الإجراءات لإضافة العد التنازلي
            let dateCell = actionsCell;
            
            if (dateCell) {
                console.log("تم العثور على خلية مناسبة للعد التنازلي");
                
                // التحقق من وجود عنصر العد التنازلي
                let countdownContainer = dateCell.querySelector('.countdown-container');
                
                if (!countdownContainer) {
                    console.log("إنشاء عنصر العد التنازلي");
                    countdownContainer = document.createElement('div');
                    countdownContainer.className = 'countdown-container';
                    
                    // إضافة العد التنازلي بجانب زر الدفع
                    const paymentButton = actionButtons.querySelector('.btn-pay');
                    if (paymentButton) {
                        countdownContainer.className = 'countdown-container ms-2 d-inline-block';
                        paymentButton.after(countdownContainer);
                    } else {
                        // في حالة عدم وجود زر الدفع، أضف العد التنازلي إلى خلية الإجراءات
                        dateCell.appendChild(countdownContainer);
                    }
                }
                
                // تحديث العد التنازلي
                function updateCountdown() {
                    const now = new Date();
                    const remainingTime = expiryDate - now;
                    
                    // تحديد اللغة بعدة طرق للتأكد من الاكتشاف الصحيح
                    const htmlLang = document.documentElement.lang;
                    const bodyDir = document.body.getAttribute('dir');
                    const hasEnglishText = statusText.includes('Confirmed') || statusText.includes('Pending');
                    const hasArabicText = statusText.includes('تم التأكيد') || statusText.includes('قيد الانتظار');
                    
                    console.log(`لغة HTML: ${htmlLang}, اتجاه الصفحة: ${bodyDir}, نص إنجليزي: ${hasEnglishText}, نص عربي: ${hasArabicText}`);
                    
                    // تحديد اللغة بناءً على عدة عوامل
                    const isEnglish = (htmlLang === 'en') || 
                                     (bodyDir !== 'rtl') || 
                                     (hasEnglishText && !hasArabicText);
                    
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
                    
                    // نعدل طريقة العرض ليناسب موقع العد بجانب زر الدفع
                    countdownContainer.innerHTML = `
                        <div class="${colorClass} fw-bold d-inline-block ms-2 me-2">
                            <i class="fas fa-clock me-1"></i>
                            ${countdownText}
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