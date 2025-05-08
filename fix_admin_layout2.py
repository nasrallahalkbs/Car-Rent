"""
إضافة زر تبديل اللغة إلى قالب admin_layout.html
"""


def add_language_toggle_to_admin_layout():
    with open('templates/admin_layout.html', 'r') as file:
        content = file.read()

    # نبحث عن مكان عنصر التبديل إلى الوضع الداكن
    dark_mode_toggle_section = """                    <!-- Dark Mode Toggle -->
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'toggle_dark_mode' %}" id="darkModeToggle">
                            {% if dark_mode %}
                            <i class="fas fa-sun"></i>
                            {% else %}
                            <i class="fas fa-moon"></i>
                            {% endif %}
                        </a>
                    </li>
                    """

    # إنشاء عنصر جديد لتبديل اللغة
    language_toggle_section = """                    <!-- Language Toggle -->
                    <li class="nav-item">
                        <a class="nav-link btn btn-sm btn-outline-primary mx-2 px-3" href="{% url 'toggle_language' %}">
                            <i class="fas fa-language {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> 
                            {% if is_english %}التحويل إلى العربية{% else %}Switch to English{% endif %}
                        </a>
                    </li>
                    """

    # إضافة عنصر تبديل اللغة بعد عنصر تبديل الوضع الداكن
    updated_content = content.replace(
        dark_mode_toggle_section,
        dark_mode_toggle_section + language_toggle_section)

    # إضافة فئات ms-1 أو me-1 إلى أيقونات القائمة تبعًا للغة
    updated_content = updated_content.replace(
        '<i class="fas fa-home ms-1"></i> الرئيسية',
        '<i class="fas fa-home {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}Home{% else %}الرئيسية{% endif %}'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-car ms-1"></i> ادارة السيارات',
        '<i class="fas fa-car {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}Cars{% else %}السيارات{% endif %}'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-bookmark ms-1"></i> حجوزاتي',
        '<i class="fas fa-bookmark {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}My Reservations{% else %}حجوزاتي{% endif %}'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-info-circle ms-1"></i> من نحن',
        '<i class="fas fa-info-circle {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}About Us{% else %}من نحن{% endif %}'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-envelope ms-1"></i> اتصل بنا',
        '<i class="fas fa-envelope {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}Contact Us{% else %}اتصل بنا{% endif %}'
    )

    # إضافة فئات ms-1 أو me-1 إلى أيقونات القائمة في الشريط الجانبي الإداري
    updated_content = updated_content.replace(
        '<i class="fas fa-tachometer-alt ms-2"></i> لوحة التحكم',
        '<i class="fas fa-tachometer-alt {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Dashboard{% else %}لوحة التحكم{% endif %}'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-car ms-2"></i> ادارة السيارات',
        '<i class="fas fa-car {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Cars{% else %}السيارات{% endif %}'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-calendar-alt ms-2"></i> الحجوزات',
        '<i class="fas fa-calendar-alt {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Reservations{% else %}الحجوزات{% endif %}'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-users ms-2"></i> المستخدمين',
        '<i class="fas fa-users {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Users{% else %}المستخدمين{% endif %}'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-credit-card ms-2"></i> المدفوعات',
        '<i class="fas fa-credit-card {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Payments{% else %}المدفوعات{% endif %}'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-sign-out-alt ms-2"></i> تسجيل الخروج',
        '<i class="fas fa-sign-out-alt {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Logout{% else %}تسجيل الخروج{% endif %}'
    )

    # تحديث الأيقونات في الوضع الداكن
    updated_content = updated_content.replace(
        '<i class="fas fa-sun"></i>',
        '<i class="fas fa-sun {% if is_english %}me-1{% else %}ms-1{% endif %}"></i>'
    )
    updated_content = updated_content.replace(
        '<i class="fas fa-moon"></i>',
        '<i class="fas fa-moon {% if is_english %}me-1{% else %}ms-1{% endif %}"></i>'
    )

    # حفظ الملف بعد التحديث
    with open('templates/admin_layout.html', 'w') as file:
        file.write(updated_content)

    print("تم إضافة زر تبديل اللغة إلى قالب admin_layout.html")


if __name__ == "__main__":
    add_language_toggle_to_admin_layout()
