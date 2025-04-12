"""
تحديث قالب التأكيد لعرض خيارات الضمان الجديدة فقط
"""

def fix_confirmation_template():
    """
    تحديث قالب التأكيد ليعرض فقط خيارات الضمان المتاحة: وديعة، بطاقة ائتمان، مستند عقاري
    """
    with open('templates/confirmation_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # استبدال الأجزاء التي تعرض خيارات الضمان بالنسخة المحدثة
    updated_content = content.replace(
        """                                {% if reservation.guarantee_type == 'id_card' %}{% trans "National ID Card" %}
                                {% elif reservation.guarantee_type == 'passport' %}{% trans "Passport" %}
                                {% elif reservation.guarantee_type == 'driving_license' %}{% trans "Driving License" %}
                                {% elif reservation.guarantee_type == 'deposit' %}{% trans "Security Deposit" %}
                                {% elif reservation.guarantee_type == 'credit_card' %}{% trans "Credit Card Hold" %}""",
        """                                {% if reservation.guarantee_type == 'deposit' %}{% trans "Security Deposit" %}
                                {% elif reservation.guarantee_type == 'credit_card' %}{% trans "Credit Card Hold" %}
                                {% elif reservation.guarantee_type == 'property_doc' %}{% trans "Property Document" %}"""
    )
    
    with open('templates/confirmation_django.html', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث قالب التأكيد بنجاح")

if __name__ == "__main__":
    fix_confirmation_template()