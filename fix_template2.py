import os
import re

# Templates to fix
templates = ['templates/cars.html', 'templates/index.html', 'templates/login.html', 'templates/register.html']

for template_path in templates:
    with open(template_path, 'r') as file:
        content = file.read()
    
    # Replace url_for with url tag
    url_for_pattern = re.compile(r'url_for\([\'"]([^\'"]+)[\'"](?:, ([^\)]+))?\)')
    
    def replace_url_for(match):
        route = match.group(1)
        args = match.group(2)
        
        if args:
            # Handle parameters like car_id=car.id
            # In Django, it would be {% url 'route' car.id %}
            params = args.split('=')
            if len(params) > 1:
                param_value = params[1].strip()
                return f"{{% url '{route}' {param_value} %}}"
        
        return f"{{% url '{route}' %}}"
    
    content = url_for_pattern.sub(replace_url_for, content)
    
    # Replace current_user with user
    content = content.replace('current_user', 'user')
    
    # Replace filters
    content = content.replace('|round', '|floatformat:0')
    content = content.replace('|capitalize', '|title')
    
    # Write back to file
    with open(template_path, 'w') as file:
        file.write(content)
    
    print(f"Fixed {template_path}")

print("All templates fixed.")
