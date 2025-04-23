"""
إصلاح مشكلة عدم استجابة المجلدات والملفات للنقرات في صفحة الأرشيف
"""

def fix_archive_folder_clicks():
    """
    إصلاح مشكلة عدم استجابة المجلدات والملفات للنقرات في صفحة الأرشيف
    
    المشكلة: الأحداث onclick لا تعمل بشكل صحيح في صفحة الأرشيف
    الحل: إصلاح وتحسين كود JavaScript المسؤول عن معالجة أحداث النقر
    """
    import os
    
    # مسار قالب الأرشيف
    template_path = "templates/admin/archive/archive_direct.html"
    
    # التأكد من وجود الملف
    if not os.path.exists(template_path):
        print(f"خطأ: لم يتم العثور على ملف القالب: {template_path}")
        return False
    
    # قراءة محتوى ملف القالب
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # إصلاح دالة showFolderContent لإضافة معالجة الأخطاء ورسائل تصحيح
    old_function = """function showFolderContent(folderId, folderName) {
    console.log('عرض محتوى المجلد: ' + folderId + ' - ' + folderName);
    
    // تحديث العنوان
    updateAddressBar(folderName);
    
    // الحصول على محتوى المجلد
    const folderContent = FOLDER_CONTENTS[folderId] || [];
    
    // عرض محتوى المجلد
    renderFolderContents(folderContent);
    
    // تسجيل هذا التنقل
    recordNavigation(folderId, folderName);
}"""

    new_function = """function showFolderContent(folderId, folderName) {
    console.log('عرض محتوى المجلد: ' + folderId + ' - ' + folderName);
    
    try {
        // تحديث العنوان
        updateAddressBar(folderName);
        
        // الحصول على محتوى المجلد
        const folderContent = FOLDER_CONTENTS[folderId] || [];
        console.log('محتوى المجلد:', folderContent);
        
        // عرض محتوى المجلد
        renderFolderContents(folderContent);
        
        // تسجيل هذا التنقل
        recordNavigation(folderId, folderName);
        
        // تحديث حالة واجهة المستخدم
        updateUIState(folderId);
        
        return true;
    } catch (error) {
        console.error('خطأ في عرض محتوى المجلد:', error);
        alert('حدث خطأ أثناء محاولة فتح المجلد. يرجى المحاولة مرة أخرى.');
        return false;
    }
}"""

    # إضافة دالة updateUIState الجديدة قبل دالة switchToGridView
    old_segment = """// تبديل طريقة العرض إلى الشبكة
function switchToGridView() {"""

    new_segment = """// تحديث حالة واجهة المستخدم بناءً على المجلد الحالي
function updateUIState(currentFolderId) {
    // تحديث الفئة النشطة للمجلدات في الوصول السريع
    document.querySelectorAll('.quick-access-item').forEach(item => {
        const folderId = item.getAttribute('data-folder-id');
        if (folderId === currentFolderId) {
            item.classList.add('active');
            item.style.backgroundColor = '#e7f1fb';
        } else {
            item.classList.remove('active');
            item.style.backgroundColor = '';
        }
    });
    
    // تمكين زر العودة إذا لم نكن في الصفحة الرئيسية
    const backBtn = document.getElementById('back-btn');
    const upBtn = document.getElementById('up-btn');
    
    if (currentFolderId && currentFolderId !== 'home') {
        backBtn.classList.remove('disabled');
        upBtn.classList.remove('disabled');
    } else {
        backBtn.classList.add('disabled');
        upBtn.classList.add('disabled');
    }
}

// تبديل طريقة العرض إلى الشبكة
function switchToGridView() {"""

    # تحسين دالة renderFolderContents لإضافة معالجة أفضل للأحداث
    old_render = """function renderFolderContents(items) {
    // الحصول على عناصر العرض
    const gridView = document.getElementById('grid-view');
    const listViewBody = document.querySelector('#list-view tbody');
    
    // تنظيف العروض الحالية
    gridView.innerHTML = '';
    listViewBody.innerHTML = '';
    
    // إذا كانت القائمة فارغة، أظهر رسالة
    if (items.length === 0) {
        gridView.innerHTML = `
            <div class="text-center p-5">
                <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">هذا المجلد فارغ</h5>
            </div>
        `;
        
        // تحديث عدد العناصر
        document.querySelector('.item-count').textContent = '0 عنصر';
        return;
    }"""

    new_render = """function renderFolderContents(items) {
    console.log('عرض محتويات المجلد:', items);
    
    // الحصول على عناصر العرض
    const gridView = document.getElementById('grid-view');
    const listViewBody = document.querySelector('#list-view tbody');
    
    if (!gridView || !listViewBody) {
        console.error('لم يتم العثور على عناصر العرض المطلوبة!');
        return;
    }
    
    // تنظيف العروض الحالية
    gridView.innerHTML = '';
    listViewBody.innerHTML = '';
    
    // إذا كانت القائمة فارغة، أظهر رسالة
    if (!items || items.length === 0) {
        gridView.innerHTML = `
            <div class="text-center p-5">
                <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">هذا المجلد فارغ</h5>
            </div>
        `;
        
        // تحديث عدد العناصر
        const itemCountElement = document.querySelector('.item-count');
        if (itemCountElement) {
            itemCountElement.textContent = '0 عنصر';
        }
        return;
    }"""

    # تحسين تعريف الأحداث للمجلدات
    old_folder_event = """folderElement.addEventListener('click', function() {
                showFolderContent(item.id, item.name);
            });"""

    new_folder_event = """folderElement.addEventListener('click', function(event) {
                event.preventDefault();
                console.log('تم النقر على المجلد:', item.id, item.name);
                showFolderContent(item.id, item.name);
            });
            
            // إضافة تأثير عند النقر لتحسين تجربة المستخدم
            folderElement.addEventListener('mousedown', function() {
                this.style.transform = 'scale(0.95)';
            });
            
            folderElement.addEventListener('mouseup', function() {
                this.style.transform = '';
            });
            
            folderElement.addEventListener('mouseleave', function() {
                this.style.transform = '';
            });"""

    # تحسين التهيئة الأولية عند تحميل الصفحة
    old_document_ready = """document.addEventListener('DOMContentLoaded', function() {
    // تبديل عرض القائمة/الشبكة
    document.getElementById('grid-view-btn').addEventListener('click', switchToGridView);
    document.getElementById('list-view-btn').addEventListener('click', switchToListView);
    
    // عرض المحتوى الافتراضي
    showDefaultContent();"""

    new_document_ready = """document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل صفحة الأرشيف');
    
    try {
        // تبديل عرض القائمة/الشبكة
        const gridViewBtn = document.getElementById('grid-view-btn');
        const listViewBtn = document.getElementById('list-view-btn');
        
        if (gridViewBtn && listViewBtn) {
            gridViewBtn.addEventListener('click', switchToGridView);
            listViewBtn.addEventListener('click', switchToListView);
        } else {
            console.warn('لم يتم العثور على أزرار تبديل طريقة العرض');
        }
        
        // إضافة مستمعات الأحداث للمجلدات في الوصول السريع
        document.querySelectorAll('.quick-access-item').forEach(item => {
            const folderId = item.getAttribute('data-folder-id');
            const folderName = item.querySelector('span').textContent;
            
            item.addEventListener('click', function(event) {
                event.preventDefault();
                console.log('تم النقر على عنصر الوصول السريع:', folderId, folderName);
                showFolderContent(folderId, folderName);
            });
        });
        
        // عرض المحتوى الافتراضي
        console.log('عرض المحتوى الافتراضي');
        showDefaultContent();"""

    # استبدال الأجزاء القديمة بالأجزاء الجديدة
    content = content.replace(old_function, new_function)
    content = content.replace(old_segment, new_segment)
    content = content.replace(old_render, new_render)
    content = content.replace(old_folder_event, new_folder_event)
    content = content.replace(old_document_ready, new_document_ready)
    
    # كتابة المحتوى المحدث إلى الملف
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"تم تحديث ملف القالب بنجاح: {template_path}")
    return True

def main():
    """
    الدالة الرئيسية لتنفيذ الإصلاحات
    """
    print("بدء إصلاح مشكلة عدم استجابة المجلدات والملفات للنقرات في صفحة الأرشيف...")
    
    result = fix_archive_folder_clicks()
    
    if result:
        print("تم إصلاح مشكلة استجابة المجلدات والملفات في صفحة الأرشيف بنجاح!")
    else:
        print("حدث خطأ أثناء محاولة إصلاح المشكلة.")

if __name__ == "__main__":
    main()