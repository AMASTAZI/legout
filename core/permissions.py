from functools import wraps
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy

class BaseRoleRequiredMixin(AccessMixin):
    """
    Mixin de base vérifiant le rôle en base de données à chaque requête HTTP.
    Empêche qu'un utilisateur n'ayant pas le rôle approprié n'accède à une vue protégée,
    même s'il saisit directement l'URL.
    """
    allowed_roles = []
    permission_denied_message = "Accès non autorisé pour votre profil utilisateur."

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        user_role = request.user.role
        is_admin_or_super = request.user.role == 'admin' or request.user.is_superuser

        # L'administrateur a un accès étendu de supervision, sinon le rôle doit correspondre exactement
        if user_role not in self.allowed_roles and not is_admin_or_super:
            messages.error(request, self.permission_denied_message)
            return redirect('dashboard:dispatch')

        return super().dispatch(request, *args, **kwargs)


class RestaurateurRequiredMixin(BaseRoleRequiredMixin):
    """Accès réservé exclusivement aux restaurateurs partenaires"""
    allowed_roles = ['restaurant', 'restaurateur']
    permission_denied_message = "Accès réservé exclusivement aux restaurateurs partenaires."


class LivreurRequiredMixin(BaseRoleRequiredMixin):
    """Accès réservé exclusivement aux livreurs partenaires"""
    allowed_roles = ['driver', 'livreur']
    permission_denied_message = "Accès réservé exclusivement aux livreurs partenaires."


class AdminRequiredMixin(BaseRoleRequiredMixin):
    """Accès réservé aux administrateurs de la plateforme"""
    allowed_roles = ['admin']
    permission_denied_message = "Accès restreint aux administrateurs de Le Gout."


class ClientRequiredMixin(BaseRoleRequiredMixin):
    """Accès réservé aux clients"""
    allowed_roles = ['client']
    permission_denied_message = "Accès réservé aux clients."


# Décorateurs de vues fonctionnelles pour un contrôle strict à chaque requête

def role_required(allowed_roles, message="Accès non autorisé pour votre profil."):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/comptes/connexion/?next={request.path}")
            
            user_role = request.user.role
            is_admin_or_super = (user_role == 'admin' or request.user.is_superuser)

            if user_role not in allowed_roles and not is_admin_or_super:
                messages.error(request, message)
                return redirect('dashboard:dispatch')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def restaurateur_required(view_func):
    return role_required(['restaurant', 'restaurateur'], "Accès réservé exclusivement aux restaurateurs.")(view_func)

def livreur_required(view_func):
    return role_required(['driver', 'livreur'], "Accès réservé exclusivement aux livreurs.")(view_func)

def admin_required(view_func):
    return role_required(['admin'], "Accès réservé à l'administration de la plateforme.")(view_func)

def client_required(view_func):
    return role_required(['client'], "Accès réservé aux clients.")(view_func)
