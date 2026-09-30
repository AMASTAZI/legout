from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('ajouter/<slug:restaurant_slug>/', views.add_review, name='add'),
    path('ajouter-avis/<slug:restaurant_slug>/', views.add_review, name='add_review'),
]
