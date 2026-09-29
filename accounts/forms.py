from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class ClientRegisterForm(forms.ModelForm):
    """
    Formulaire public d'inscription STRICTEMENT réservé aux clients.
    Le champ 'role' est TOTALEMENT ABSENT des champs autorisés.
    La valeur role='client' est impérativement verrouillée côté serveur.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]',
            'placeholder': 'Mot de passe sécurisé'
        }),
        label="Mot de passe"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]',
            'placeholder': 'Confirmez votre mot de passe'
        }),
        label="Confirmation du mot de passe"
    )

    class Meta:
        model = User
        # EXCLUSION STRICTE DU CHAMP 'role' POUR EMPÊCHER TOUTE ÉLÉVATION DE PRIVILÈGES
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'city', 'neighborhood', 'address_details']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': 'Identifiant unique'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': 'votre.email@domaine.cm'}),
            'phone': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': '+237 699 00 11 22'}),
            'city': forms.Select(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'neighborhood': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': 'Ex: Akwa, Bonapriso, Deido...'}),
            'address_details': forms.Textarea(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'rows': 2, 'placeholder': 'Ex: Face boulangerie du rond-point, portail marron'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Les deux mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Rôle inaltérable et forcé côté serveur
        user.role = 'client'
        user.must_change_password = False
        user.wallet_balance = 10000  # Bonus de bienvenue simulé offert
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AdminStaffCreateForm(forms.ModelForm):
    """
    Formulaire réservé à l'Administrateur pour créer les comptes Restaurateur et Livreur.
    Définit un mot de passe temporaire et active must_change_password=True.
    """
    STAFF_ROLE_CHOICES = [
        ('restaurateur', 'Restaurateur / Gérant'),
        ('livreur', 'Livreur Partenaire'),
    ]

    role = forms.ChoiceField(
        choices=STAFF_ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
        label="Rôle attribué"
    )
    temporary_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]',
            'placeholder': 'Mot de passe temporaire'
        }),
        label="Mot de passe temporaire"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'city', 'neighborhood', 'address_details']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': 'Identifiant'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': 'email@pro.cm'}),
            'phone': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'placeholder': '+237 690 00 00 00'}),
            'city': forms.Select(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'neighborhood': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'address_details': forms.Textarea(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'rows': 2}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['temporary_password'])
        # Obligation de changer de mot de passe à la 1ère connexion
        user.must_change_password = True
        user.is_staff = (self.cleaned_data['role'] == 'restaurateur')
        if commit:
            user.save()
        return user


class ForcePasswordChangeForm(forms.Form):
    """Formulaire de changement de mot de passe obligatoire dès la 1ère connexion"""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]',
            'placeholder': 'Nouveau mot de passe personnel'
        }),
        label="Nouveau mot de passe"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]',
            'placeholder': 'Confirmez le nouveau mot de passe'
        }),
        label="Confirmation du mot de passe"
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Les deux nouveaux mots de passe ne correspondent pas.")
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'neighborhood', 'address_details']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'phone': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'city': forms.Select(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'neighborhood': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'address_details': forms.Textarea(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'rows': 3}),
        }

# Alias de compatibilité
RegisterForm = ClientRegisterForm
