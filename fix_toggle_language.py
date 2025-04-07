"""
إعادة دالة toggle_language إلى الإصدار الأصلي البسيط
"""

import os
import sys

def main():
    """
    تحديث ملف views.py بوظيفة toggle_language أبسط
    """
    # قراءة ملف views.py
    views_path = "rental/views.py"
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # البحث عن دالة toggle_language وتعديلها
    start_marker = "def toggle_language(request):"
    function_start = content.find(start_marker)
    
    if function_start == -1:
        print("لم يتم العثور على دالة toggle_language")
        return
    
    # البحث عن نهاية الدالة (الدالة التالية)
    next_function = content.find("def ", function_start + len(start_marker))
    
    if next_function == -1:
        print("لم يتم العثور على نهاية دالة toggle_language")
        return
    
    # استبدال الدالة بالإصدار البسيط
    simple_toggle_function = """def toggle_language(request):
    \"\"\"Toggle between Arabic and English languages\"\"\"
    current_language = request.session.get('language', 'ar')  # Default to Arabic if not set
    
    # Toggle between 'ar' and 'en'
    new_language = 'en' if current_language == 'ar' else 'ar'
    request.session['language'] = new_language
    
    # Force save session to ensure changes are persisted
    request.session.modified = True
    
    # Add success message
    if new_language == 'ar':
        messages.success(request, "تم تغيير اللغة إلى العربية")
    else:
        messages.success(request, "Language changed to English successfully")
    
    # Go back to the previous page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('index')
"""
    
    # تحديث المحتوى
    new_content = content[:function_start] + simple_toggle_function + content[next_function:]
    
    # كتابة الملف المحدث
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("تم تحديث دالة toggle_language بنجاح")

if __name__ == "__main__":
    main()