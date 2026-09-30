from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    path('', views.restaurant_list, name='list'),
    path('produit/<slug:slug>/', views.dish_detail, name='dish_detail'),
    path('<slug:slug>/', views.restaurant_detail, name='detail'),
]
