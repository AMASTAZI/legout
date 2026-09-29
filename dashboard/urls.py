from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_dispatch, name='dispatch'),
    
    # 1. Espace Restaurateur
    path('restaurant/', views.restaurant_overview, name='restaurant'),
    path('restaurant/commandes/', views.restaurant_orders, name='restaurant_orders'),
    path('restaurant/commandes/<int:order_id>/statut/', views.restaurant_update_order_status, name='restaurant_order_status'),
    path('restaurant/commandes/<int:order_id>/valider/', views.restaurant_validate_order, name='restaurant_validate_order'),
    path('restaurant/commandes/<int:order_id>/refuser/', views.restaurant_refuse_order, name='restaurant_refuse_order'),
    path('restaurant/menu/', views.restaurant_menu, name='restaurant_menu'),
    path('restaurant/menu/dispo/<int:dish_id>/', views.restaurant_toggle_dish, name='restaurant_toggle_dish'),
    path('restaurant/menu/ajouter/', views.restaurant_add_dish, name='restaurant_add_dish'),
    path('restaurant/menu/modifier/<int:dish_id>/', views.restaurant_edit_dish, name='restaurant_edit_dish'),
    path('restaurant/menu/supprimer/<int:dish_id>/', views.restaurant_delete_dish, name='restaurant_delete_dish'),
    path('restaurant/parametres/', views.restaurant_settings, name='restaurant_settings'),

    # 2. Espace Livreur
    path('livreur/', views.driver_overview, name='driver'),
    path('livreur/accepter/<int:delivery_id>/', views.driver_accept_delivery, name='driver_accept'),
    path('livreur/active/', views.driver_active, name='driver_active'),
    path('livreur/etape/<int:delivery_id>/', views.driver_update_status, name='driver_status'),
    path('livreur/gps/<int:delivery_id>/', views.driver_update_gps, name='driver_update_gps'),
    path('livreur/gains/', views.driver_earnings, name='driver_earnings'),

    # 3. Espace Administrateur
    path('admin/', views.admin_overview, name='admin'),
    path('admin/utilisateurs/', views.admin_users, name='admin_users'),
    path('admin/utilisateurs/creer/', views.admin_create_staff_user, name='admin_create_staff'),
    path('admin/utilisateurs/<int:user_id>/toggle/', views.admin_toggle_user_active, name='admin_toggle_user_active'),
    path('admin/utilisateurs/<int:user_id>/supprimer/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/restaurant/', views.admin_restaurant_settings, name='admin_restaurant_settings'),
]
