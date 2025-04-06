with open('templates/layout.html', 'r') as file:
    content = file.read()

# استبدال عبارات url_for للملفات الثابتة
content = content.replace("{{ url_for('static', filename='css/style.css') }}", "{% static 'css/style.css' %}")
content = content.replace("{{ url_for('static', filename='css/dark-mode.css') }}", "{% static 'css/dark-mode.css' %}")
content = content.replace("{{ url_for('static', filename='js/scripts.js') }}", "{% static 'js/scripts.js' %}")
content = content.replace("{{ url_for('static', filename='js/dark-mode.js') }}", "{% static 'js/dark-mode.js' %}")

# استبدال عبارات url_for للروابط
content = content.replace("{{ url_for('index') }}", "{% url 'index' %}")
content = content.replace("{{ url_for('car_listing') }}", "{% url 'car_listing' %}")
content = content.replace("{{ url_for('admin_index') }}", "{% url 'admin_index' %}")
content = content.replace("{{ url_for('cart') }}", "{% url 'cart' %}")
content = content.replace("{{ url_for('profile') }}", "{% url 'profile' %}")
content = content.replace("{{ url_for('my_reservations') }}", "{% url 'my_reservations' %}")
content = content.replace("{{ url_for('logout') }}", "{% url 'logout' %}")
content = content.replace("{{ url_for('login') }}", "{% url 'login' %}")
content = content.replace("{{ url_for('register') }}", "{% url 'register' %}")
content = content.replace("{{ url_for('toggle_dark_mode') }}", "{% url 'toggle_dark_mode' %}")

# استبدال current_user بـ user وهو المتغير الذي يحتوي على المستخدم الحالي في Django
content = content.replace("current_user", "user")

# استبدال عبارات get_flashed_messages بـ messages وهو المتغير الذي يحتوي على الرسائل في Django
content = content.replace("{% with messages = get_flashed_messages(with_categories=true) %}", "")
content = content.replace("{% endwith %}", "")

# إضافة load static في بداية الملف
content = "{% load static %}\n" + content

with open('templates/layout.html', 'w') as file:
    file.write(content)

print("Fixed layout.html")
