from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login as auth_login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import ClientRegisterForm, ProfileForm, ForcePasswordChangeForm

User = get_user_model()

def determine_role_redirect_url(user, next_url=None, allowed_hosts=None):
    """
    Fonction centralisée de redirection exécutée STRICTEMENT côté backend
    selon le rôle réel persisté en base de données et l'état du compte.
    """
    # 1. Si le compte a été créé par l'admin avec obligation de renouveler son mot de passe
    if getattr(user, 'must_change_password', False):
        return reverse_lazy('accounts:force_password_change')

    # 2. Si le client avait demandé une page spécifique protégée (ex: panier ou checkout)
    if next_url and allowed_hosts and url_has_allowed_host_and_scheme(next_url, allowed_hosts=allowed_hosts):
        return next_url

    # 3. Aiguillage automatique selon le rôle en base
    role = user.role
    if user.is_superuser or role == 'admin':
        return reverse_lazy('dashboard:admin')
    elif role in ['restaurant', 'restaurateur']:
        return reverse_lazy('dashboard:restaurant')
    elif role in ['driver', 'livreur']:
        return reverse_lazy('dashboard:driver')
    else:  # client
        return reverse_lazy('orders:cart')


class CustomLoginView(LoginView):
    """
    Vue de connexion unique pour tous les rôles.
    La détection du rôle et la redirection sont gérées STRICTEMENT côté backend.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        target_url = determine_role_redirect_url(
            user,
            next_url=next_url,
            allowed_hosts={self.request.get_host()}
        )
        return str(target_url)

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f"Connexion réussie ! Bienvenue {user.get_full_name() or user.username} ({user.get_role_display()}).")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # RÈGLE DU PROJET : Les boutons démo pré-remplissent seulement les identifiants
        # de comptes réels en base et sont STRICTEMENT réservés à l'environnement DEBUG.
        if settings.DEBUG:
            real_accounts = []
            admin_u = User.objects.filter(role='admin').first() or User.objects.filter(is_superuser=True).first()
            if admin_u:
                real_accounts.append({'label': f'Admin ({admin_u.username})', 'username': admin_u.username, 'role_badge': 'Admin'})
            
            resto_u = User.objects.filter(role__in=['restaurateur', 'restaurant']).first()
            if resto_u:
                real_accounts.append({'label': f'Restaurateur ({resto_u.username})', 'username': resto_u.username, 'role_badge': 'Restaurateur'})
            
            driver_u = User.objects.filter(role__in=['livreur', 'driver']).first()
            if driver_u:
                real_accounts.append({'label': f'Livreur ({driver_u.username})', 'username': driver_u.username, 'role_badge': 'Livreur'})
            
            client_u = User.objects.filter(role='client').first()
            if client_u:
                real_accounts.append({'label': f'Client ({client_u.username})', 'username': client_u.username, 'role_badge': 'Client'})
            
            context['demo_accounts'] = real_accounts
            context['is_debug'] = True
        else:
            context['demo_accounts'] = []
            context['is_debug'] = False
        return context


def register_view(request):
    """
    Inscription publique STRICTEMENT réservée aux clients.
    Le champ 'role' est impossible à manipuler (absent du formulaire, forcé côté serveur).
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dispatch')

    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            # Sauvegarde avec rôle 'client' forcé de manière immuable
            user = form.save()
            messages.success(request, f"Bienvenue {user.first_name or user.username} ! Votre compte Client a été créé avec succès.")
            auth_login(request, user, backend='accounts.backends.EmailOrUsernameModelBackend')
            target = determine_role_redirect_url(user)
            return redirect(target)
        else:
            messages.error(request, "Veuillez corriger les informations saisies.")
    else:
        form = ClientRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def force_password_change_view(request):
    """
    Redirection forcée lors de la première connexion pour tout compte créé
    par l'administrateur avec un mot de passe temporaire.
    """
    if not request.user.must_change_password:
        return redirect(determine_role_redirect_url(request.user))

    if request.method == 'POST':
        form = ForcePasswordChangeForm(request.POST)
        if form.is_valid():
            new_pass = form.cleaned_data['new_password']
            request.user.set_password(new_pass)
            request.user.must_change_password = False
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Votre mot de passe personnel a été enregistré avec succès. Bienvenue sur votre espace de travail !")
            return redirect(determine_role_redirect_url(request.user))
    else:
        form = ForcePasswordChangeForm()

    return render(request, 'accounts/force_password_change.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès. À bientôt chez Le Gout !")
    return redirect('core:home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos coordonnées ont été mises à jour avec succès.")
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
