"""
إصلاح قسم "تصفح حسب الفئة" في الصفحة الرئيسية لدعم اللغتين العربية والإنجليزية
"""

def fix_index_categories():
    with open('templates/index_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث عنوان قسم "تصفح حسب الفئة"
    content = content.replace(
        '<h2 class="section-title">تصفح حسب الفئة</h2>',
        '<h2 class="section-title">{% if is_english %}Browse by Category{% else %}تصفح حسب الفئة{% endif %}</h2>'
    )
    
    # تحديث نص "عرض الكل" إذا موجود
    content = content.replace(
        '<span class="view-all">عرض الكل</span>',
        '<span class="view-all">{% if is_english %}View All{% else %}عرض الكل{% endif %}</span>'
    )
    
    # تحديث نص "السيارات المتوفرة" إذا موجود
    content = content.replace(
        '<p class="cars-count">{{ cars|length }} سيارات متوفرة</p>',
        '<p class="cars-count">{{ cars|length }} {% if is_english %}available cars{% else %}سيارات متوفرة{% endif %}</p>'
    )
    
    # تحديث أسماء الفئات إذا موجودة كنصوص ثابتة
    # مثال: Economy, Compact, لخ
    category_translations = [
        ('اقتصادية', 'Economy'),
        ('مدمجة', 'Compact'),
        ('متوسطة', 'Mid-size'),
        ('فاخرة', 'Luxury'),
        ('سيارات الدفع الرباعي', 'SUVs'),
        ('سيارات رياضية', 'Sports Cars'),
        ('شاحنات', 'Trucks'),
        ('الكهربائية', 'Electric'),
        ('الهجينة', 'Hybrid')
    ]
    
    for ar, en in category_translations:
        content = content.replace(
            f'<div class="category-name">{ar}</div>',
            f'<div class="category-name">{{% if is_english %}}{en}{{% else %}}{ar}{{% endif %}}</div>'
        )
    
    # حفظ التغييرات
    with open('templates/index_django.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("تم تحديث قسم 'تصفح حسب الفئة' في الصفحة الرئيسية بنجاح")

if __name__ == "__main__":
    fix_index_categories()
