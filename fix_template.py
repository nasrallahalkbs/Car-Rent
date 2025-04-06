with open('templates/admin/index.html', 'r') as file:
    content = file.read()

content = content.replace('<span class="badge bg-{{ \'success\' if item.reservation.status == \'confirmed\' else \'warning\' if item.reservation.status == \'pending\' else \'info\' if item.reservation.status == \'completed\' else \'danger\' }}">', '<span class="badge {% if item.reservation.status == \'confirmed\' %}bg-success{% elif item.reservation.status == \'pending\' %}bg-warning{% elif item.reservation.status == \'completed\' %}bg-info{% else %}bg-danger{% endif %}">')

with open('templates/admin/index.html', 'w') as file:
    file.write(content)

print("Fixed index.html")
