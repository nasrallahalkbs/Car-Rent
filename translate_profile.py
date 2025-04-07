#!/usr/bin/env python3

"""
Translate profile.html to Arabic.
"""

with open('templates/profile.html', 'r', encoding='utf-8') as file:
    content = file.read()

# Replace English texts with Arabic translations
translations = {
    "My Profile - CarRental": "الملف الشخصي - كاررنتال",
    "My Profile": "الملف الشخصي",
    "Email": "البريد الإلكتروني",
    "Phone": "رقم الهاتف",
    "Member Since": "عضو منذ",
    "My Reservations": "حجوزاتي",
    "Edit Profile": "تعديل الملف الشخصي",
    "Save Changes": "حفظ التغييرات",
}

for english, arabic in translations.items():
    content = content.replace(english, arabic)

# Fix date format
content = content.replace('|date:"M d, Y"', '|date:"d F Y"')

# Fix labels
content = content.replace('<label for="first_name">{{ form.first_name.label }}</label>', 
                         '<label for="first_name">الاسم الأول</label>')
content = content.replace('<label for="last_name">{{ form.last_name.label }}</label>', 
                         '<label for="last_name">اسم العائلة</label>')
content = content.replace('<label for="email">{{ form.email.label }}</label>', 
                         '<label for="email">البريد الإلكتروني</label>')
content = content.replace('<label for="phone">{{ form.phone.label }}</label>', 
                         '<label for="phone">رقم الهاتف</label>')

with open('templates/profile.html', 'w', encoding='utf-8') as file:
    file.write(content)

print("Profile template translated to Arabic successfully!")