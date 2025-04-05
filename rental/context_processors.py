from .models import CartItem

def cart_count(request):
    """Add cart_count to all templates"""
    count = 0
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    return {'cart_count': count}

def dark_mode(request):
    """Add dark_mode to all templates"""
    dark_mode = request.session.get('dark_mode', False)
    return {'dark_mode': dark_mode}