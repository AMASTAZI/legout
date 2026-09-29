from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('panier/', views.cart_view, name='cart'),
    path('panier/ajouter/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('panier/modifier/<int:dish_id>/', views.update_cart, name='update_cart'),
    path('panier/vider/', views.clear_cart, name='clear_cart'),
    path('commander/', views.checkout_view, name='checkout'),
    path('suivi/<str:order_number>/', views.order_tracking, name='tracking'),
    path('api/status/<str:order_number>/', views.order_status_api, name='status_api'),
    path('historique/', views.order_history, name='history'),
    path('facture/<str:order_number>/', views.invoice_detail_view, name='invoice_detail'),
    path('facture/<str:order_number>/pdf/', views.invoice_pdf_view, name='invoice_pdf'),
    path('annuler/<str:order_number>/', views.cancel_order, name='cancel'),
]
