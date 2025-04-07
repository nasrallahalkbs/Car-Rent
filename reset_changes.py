"""
إرجاع جميع التغييرات إلى الوضع الأصلي قبل إضافة خاصية اختيار اللغة
"""

import os
from django.shortcuts import redirect, render

def reset_toggle_language():
    """إعادة دالة toggle_language إلى الشكل الأصلي البسيط"""
    views_path = "rental/views.py"
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن الدالة وتعديلها
    simple_toggle_language = """def toggle_language(request):
    \"\"\"Toggle language settings\"\"\"
    # Toggle language in session
    language = request.session.get('language', 'ar')
    request.session['language'] = 'en' if language == 'ar' else 'ar'
    
    # Redirect back to the same page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('index')
"""
    
    # البحث عن دالة toggle_language الحالية
    start_marker = "def toggle_language(request):"
    function_start = content.find(start_marker)
    if function_start == -1:
        print("لم يتم العثور على دالة toggle_language")
        return
    
    # العثور على نهاية الدالة (بداية الدالة التالية)
    next_function = content.find("def ", function_start + len(start_marker))
    if next_function == -1:
        print("لم يتم العثور على نهاية دالة toggle_language")
        return
    
    # استبدال الدالة
    new_content = content[:function_start] + simple_toggle_language + content[next_function:]
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("تم إعادة دالة toggle_language إلى الشكل الأصلي")

def reset_index_function():
    """إعادة دالة index إلى الشكل الأصلي البسيط بدون اختيار القالب بناءً على اللغة"""
    views_path = "rental/views.py"
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # نبحث عن الجزء الذي يقوم باختيار القالب بناءً على اللغة في دالة index
    index_template_selection = """    # Choose template based on language setting
    language = request.session.get('language', 'ar')
    
    # Special case for index - uses 'index_arabic.html' instead of 'index_django.html'
    if language == 'ar':
        template = 'index_arabic.html'
    else:
        template = 'index.html'
    
    return render(request, template, context)"""
    
    # استبدال هذا الجزء بالكود الأصلي البسيط
    original_index_template = """    # Always use index.html regardless of language
    return render(request, 'index.html', context)"""
    
    # استبدال النص
    new_content = content.replace(index_template_selection, original_index_template)
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("تم إعادة دالة index إلى الشكل الأصلي")

def reset_template_selections():
    """إزالة جميع الحالات التي تختار القوالب بناءً على اللغة"""
    views_path = "rental/views.py"
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # نماذج لاستبدال اختيار القوالب بناءً على اللغة
    replacements = [
        ("    # Choose template based on language setting\n    language = request.session.get('language', 'ar')\n    template = 'cars.html' if language == 'en' else 'cars_django.html'\n    \n    return render(request, template, context)",
         "    return render(request, 'cars.html', context)"),
        
        ("    # Choose template based on language setting\n    language = request.session.get('language', 'ar')\n    template = 'car_detail.html' if language == 'en' else 'car_detail_django.html'\n    \n    return render(request, template, context)",
         "    return render(request, 'car_detail.html', context)"),
        
        ("    # Choose template based on language setting\n    language = request.session.get('language', 'ar')\n    template = 'cart.html' if language == 'en' else 'cart_django.html'\n    \n    return render(request, template, context)",
         "    return render(request, 'cart.html', context)"),
        
        ("    # Choose template based on language setting\n    language = request.session.get('language', 'ar')\n    template = 'confirmation.html' if language == 'en' else 'confirmation_django.html'\n    \n    return render(request, template, context)",
         "    return render(request, 'confirmation.html', context)"),
        
        ("    # Choose template based on language setting\n    language = request.session.get('language', 'ar')\n    template = 'my_reservations.html' if language == 'en' else 'my_reservations_django.html'\n    \n    return render(request, template, context)",
         "    return render(request, 'my_reservations.html', context)"),
        
        ("    # Choose template based on language setting\n    language = request.session.get('language', 'ar')\n    template = 'about_us.html' if language == 'en' else 'about_us_django.html'\n    \n    return render(request, template)",
         "    return render(request, 'about_us.html')"),
    ]
    
    # تطبيق جميع الاستبدالات
    new_content = content
    for old, new in replacements:
        new_content = new_content.replace(old, new)
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("تم إزالة جميع حالات اختيار القوالب بناءً على اللغة")

def main():
    """تنفيذ جميع التغييرات لإعادة الكود إلى حالته الأصلية"""
    reset_toggle_language()
    reset_index_function()
    reset_template_selections()
    print("تم إرجاع جميع التغييرات إلى الوضع الأصلي")

if __name__ == "__main__":
    main()