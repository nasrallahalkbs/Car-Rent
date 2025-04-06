with open('templates/car_detail.html', 'r') as file:
    content = file.read()

# تغيير القالب الذي يمتد منه
content = content.replace("{% extends 'layout.html' %}", "{% extends 'layout_django.html' %}\n{% load static %}")

# تغيير url_for للملفات الثابتة
content = content.replace("{{ url_for('static', filename='js/reservation.js') }}", "{% static 'js/reservation.js' %}")

# تغيير url_for للروابط
content = content.replace("{{ url_for('index') }}", "{% url 'index' %}")
content = content.replace("{{ url_for('car_listing') }}", "{% url 'car_listing' %}")
content = content.replace("{{ url_for('add_review', reservation_id=request.view_args.reservation_id) }}", 
                         "{% url 'add_review' reservation_id=request.resolver_match.kwargs.reservation_id %}")
content = content.replace("{{ url_for('car_detail', car_id=car.id) }}", "{% url 'car_detail' car_id=car.id %}")

with open('templates/car_detail.html', 'w') as file:
    file.write(content)

print("Fixed car_detail.html")
