/**
 * وظائف تحديث عدادات الصلاحيات
 * هذا الملف يحتوي على وظائف تحديث عدادات الصلاحيات في واجهة إدارة الصلاحيات المتقدمة
 */

// تحديث عدادات جميع الأقسام
function updateAllCounters() {
    console.log("🔄 تحديث جميع عدادات الصلاحيات...");
    
    // تحديث عدادات الأقسام
    $('.permissions-section').each(function() {
        const sectionId = $(this).attr('id');
        if (!sectionId) return;
        
        const sectionName = sectionId.replace('section-', '');
        const totalCards = $(this).find('.permission-card').length;
        const activeCards = $(this).find('.permission-card.active').length;
        
        // تحديث العداد في عنوان القسم
        const sectionCount = $(this).find('.section-count');
        if (sectionCount.length) {
            sectionCount.text(`${activeCards} / ${totalCards}`);
        }
        
        // تحديث العداد في التبويب
        const tabCount = $(`.tab-item[data-section="${sectionName}"] .tab-count`);
        if (tabCount.length) {
            tabCount.text(activeCards);
            
            // إضافة تنسيق خاص إذا كان العدد صفر
            if (activeCards === 0) {
                tabCount.addClass('empty');
            } else {
                tabCount.removeClass('empty');
            }
        }
    });
    
    // تحديث العداد الإجمالي
    updateTotalCount();
}

// تحديث العداد الإجمالي في أعلى الصفحة
function updateTotalCount() {
    const totalPermissions = $('.permission-card').length;
    const activePermissions = $('.permission-card.active').length;
    
    // تحديث العداد الإجمالي إذا كان موجوداً
    const totalCounter = $('#total-permissions-counter');
    if (totalCounter.length) {
        totalCounter.text(`${activePermissions} / ${totalPermissions}`);
        
        // تحديث لون العداد حسب النسبة
        if (activePermissions === 0) {
            totalCounter.removeClass('warning success').addClass('danger');
        } else if (activePermissions < totalPermissions / 2) {
            totalCounter.removeClass('danger success').addClass('warning');
        } else {
            totalCounter.removeClass('danger warning').addClass('success');
        }
    }
}

// تحديث عداد قسم معين
function updateSectionCounter(sectionName) {
    const section = $(`#section-${sectionName}`);
    if (!section.length) {
        console.warn(`لم يتم العثور على القسم: ${sectionName}`);
        return;
    }
    
    const totalCards = section.find('.permission-card').length;
    const activeCards = section.find('.permission-card.active').length;
    
    // تحديث العداد في عنوان القسم
    const sectionCount = section.find('.section-count');
    if (sectionCount.length) {
        sectionCount.text(`${activeCards} / ${totalCards}`);
    }
    
    // تحديث العداد في التبويب
    const tabCount = $(`.tab-item[data-section="${sectionName}"] .tab-count`);
    if (tabCount.length) {
        tabCount.text(activeCards);
        
        // إضافة تنسيق خاص إذا كان العدد صفر
        if (activeCards === 0) {
            tabCount.addClass('empty');
        } else {
            tabCount.removeClass('empty');
        }
    }
}

// تحديث العدادات عند تغيير حالة بطاقة صلاحية
function updateCountersOnCardChange(card) {
    // الحصول على اسم القسم من البطاقة
    const sectionName = $(card).data('section');
    if (sectionName) {
        // تحديث عداد القسم
        updateSectionCounter(sectionName);
    }
    
    // تحديث العداد الإجمالي
    updateTotalCount();
}

// إعداد مستمعي الأحداث لبطاقات الصلاحيات
$(document).ready(function() {
    // تحديث جميع العدادات عند تحميل الصفحة
    setTimeout(updateAllCounters, 500);
    
    // إضافة مستمع للنقر على بطاقات الصلاحيات
    $(document).on('click', '.permission-card', function(e) {
        // تجاهل النقر على عناصر تفاعلية داخل البطاقة
        if ($(e.target).is('button, a, input') || $(e.target).closest('button, a, input').length) {
            return;
        }
        
        // تحديث العدادات بعد تغيير حالة البطاقة
        setTimeout(function() {
            updateCountersOnCardChange(e.currentTarget);
        }, 50);
    });
});