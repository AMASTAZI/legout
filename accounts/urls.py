from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.register_view, name='register'),
    path('connexion/', views.CustomLoginView.as_view(), name='login'),
    path('changer-mot-de-passe/', views.force_password_change_view, name='force_password_change'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
]
