/**
 * ملف JavaScript لإدارة أزرار الأرشيف الإلكتروني
 */

// عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تهيئة أزرار القائمة المنسدلة
    initDropdownMenus();
});

/**
 * تهيئة القوائم المنسدلة لأزرار التحكم
 */
function initDropdownMenus() {
    // إضافة مستمع حدث النقر لإغلاق جميع القوائم عند النقر على أي مكان في الصفحة
    document.addEventListener('click', function(event) {
        document.querySelectorAll('.item-actions.show').forEach(menu => {
            menu.classList.remove('show');
        });
    });
}

/**
 * تبديل عرض قائمة الإجراءات
 * @param {Event} event - حدث النقر
 * @param {HTMLElement} actionMenu - عنصر HTML للقائمة
 */
function toggleItemMenu(event, actionMenu) {
    // منع انتشار الحدث لتجنب النقر على العنصر نفسه
    event.stopPropagation(); 
    
    // إغلاق جميع القوائم المفتوحة أولاً
    document.querySelectorAll('.item-actions.show').forEach(menu => {
        if (menu !== actionMenu) {
            menu.classList.remove('show');
        }
    });
    
    // تبديل حالة العرض للقائمة الحالية
    actionMenu.classList.toggle('show');
}