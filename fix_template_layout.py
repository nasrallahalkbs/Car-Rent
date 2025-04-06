import re

with open('templates/layout.html', 'r') as file:
    content = file.read()

# تصحيح url_for في شروط if
content = content.replace("{% if request.path == url_for('cart') %}active{% endif %}", 
                         "{% if request.path == '/cart/' %}active{% endif %}")

content = content.replace("{% if request.path == url_for('login') %}active{% endif %}", 
                         "{% if request.path == '/login/' %}active{% endif %}")

content = content.replace("{% if request.path == url_for('register') %}active{% endif %}", 
                         "{% if request.path == '/register/' %}active{% endif %}")

content = content.replace("{% if request.path == '/' %}active{% endif %}", 
                         "{% if request.path == '/' %}active{% endif %}")

content = content.replace("{% if '/cars/' in request.path %}active{% endif %}", 
                         "{% if '/cars/' in request.path %}active{% endif %}")

content = content.replace("{% if '/admin/' in request.path %}active{% endif %}", 
                         "{% if '/admin/' in request.path %}active{% endif %}")

# البحث عن أي url_for متبقي
url_for_pattern = re.compile(r'url_for\([\'"]([^\'"]+)[\'"](?:, ([^\)]+))?\)')

def replace_url_for(match):
    route = match.group(1)
    args = match.group(2)
    
    if args:
        # إصلاح الوسائط مثل car_id=car.id
        return f"url '{route}' {args}"
    else:
        return f"url '{route}'"

# تطبيق النمط على المحتوى
content = url_for_pattern.sub(replace_url_for, content)

with open('templates/layout.html', 'w') as file:
    file.write(content)

print("Fixed layout.html")
