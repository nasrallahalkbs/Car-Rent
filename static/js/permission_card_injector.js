/**
 * سكريبت إضافة سمات بيانات إلى بطاقات الصلاحيات
 *
 * هذا السكريبت يقوم بإضافة سمات البيانات data-section و data-permission
 * إلى بطاقات الصلاحيات للاستخدام مع وظائف تحديث الصلاحيات 
 */

// تنفيذ عند اكتمال تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔍 جارٍ التحقق من بطاقات الصلاحيات وإضافة سمات البيانات...");
    
    // الحصول على جميع الأقسام
    const sections = document.querySelectorAll('.permissions-section');
    
    sections.forEach(section => {
        // استخراج معرف القسم (مثل dashboard أو customers)
        const sectionId = section.id.replace('section-', '');
        
        // الحصول على جميع بطاقات الصلاحيات في هذا القسم
        const cards = section.querySelectorAll('.permission-card');
        
        cards.forEach(card => {
            // التحقق إذا كان لدى البطاقة سمات البيانات المطلوبة
            if (!card.hasAttribute('data-section') || !card.hasAttribute('data-permission')) {
                // البحث عن اسم الصلاحية من العنصر الفرعي
                const titleElement = card.querySelector('.permission-title');
                let permissionName = '';
                
                if (titleElement && titleElement.hasAttribute('data-perm-name')) {
                    // استخدام سمة data-perm-name من العنصر الفرعي
                    permissionName = titleElement.getAttribute('data-perm-name');
                } else if (titleElement) {
                    // محاولة استنتاج الاسم من النص
                    permissionName = titleElement.textContent.trim().toLowerCase()
                        .replace(/\s+/g, '_') // استبدال المسافات بشرطة سفلية
                        .replace(/[^\w\s]/gi, '') // إزالة الأحرف الخاصة
                        .replace(/_+/g, '_'); // تجنب الشرطات المتكررة
                }
                
                // إضافة سمات البيانات إلى البطاقة
                card.setAttribute('data-section', sectionId);
                card.setAttribute('data-permission', permissionName);
                
                console.log(`✅ تمت إضافة سمات البيانات: ${sectionId}_${permissionName}`);
            }
        });
    });
    
    // التحقق من عدد البطاقات المعالجة
    const totalCards = document.querySelectorAll('.permission-card').length;
    const processedCards = document.querySelectorAll('.permission-card[data-section][data-permission]').length;
    
    console.log(`🔄 المجموع: تمت معالجة ${processedCards} بطاقة من أصل ${totalCards}`);
});