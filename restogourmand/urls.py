"""
URL configuration for restogourmand project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls), # Interface Admin Django standard
    path('admin-technique/', RedirectView.as_view(url='/admin/', permanent=False)), # Redirection automatique vers /admin/
    path('', include('core.urls')),
    path('comptes/', include('accounts.urls')),
    path('restaurants/', include('restaurants.urls')),
    path('commandes/', include('orders.urls')),
    path('avis/', include('reviews.urls')),
    path('assistant-culinaire/', include('chatbot.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
