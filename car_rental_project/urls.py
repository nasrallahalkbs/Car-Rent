from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# URLs that don't need language prefix
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switching URLs
]

# URLs with language prefix (e.g., /ar/, /en/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('rental.urls')),
    prefix_default_language=True,  # Include prefix for default language too
)

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)