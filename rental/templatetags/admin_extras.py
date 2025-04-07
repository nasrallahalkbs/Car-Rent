from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def debug_models(model_name, items):
    """
    Display debug information about models
    """
    output = f"<div style='display:none;'><h4>Debug: {model_name}</h4>"
    output += f"<p>Total items: {len(items)}</p>"
    output += "<ul>"
    for item in items:
        output += f"<li>{item}</li>"
    output += "</ul></div>"
    return mark_safe(output)

@register.filter
def debug_var(var):
    """
    Debug the value of a variable
    """
    return f"DEBUG: {var}"