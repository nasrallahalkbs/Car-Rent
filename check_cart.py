import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import CartItem, FavoriteCar
from django.contrib.auth import get_user_model

User = get_user_model()

print('المستخدمين في النظام:')
for u in User.objects.all():
    print(f'- {u.username}, المعرف: {u.id}')

print('\nعناصر السلة:')
for item in CartItem.objects.all():
    print(f'- المستخدم: {item.user.username}, السيارة: {item.car.make} {item.car.model}')

print('\nالسيارات المفضلة:')
for fav in FavoriteCar.objects.all():
    print(f'- المستخدم: {fav.user.username}, السيارة: {fav.car.make} {fav.car.model}')