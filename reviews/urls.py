from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('ajouter/<slug:restaurant_slug>/', views.add_review, name='add'),
]
