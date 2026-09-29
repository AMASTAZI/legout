from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.home, name='menu'),
    path('cgu/', views.cgu, name='cgu'),
    path('confidentialite/', views.privacy, name='privacy'),
]
