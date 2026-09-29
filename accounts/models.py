from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

class CustomUserManager(UserManager):
    """
    Manager personnalisé qui surcharge create_superuser() pour affecter
    automatiquement le rôle 'admin' lors de la commande createsuperuser.
    """
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('restaurateur', 'Restaurateur / Gérant'),
        ('livreur', 'Livreur Partenaire'),
        ('admin', 'Administrateur Plateforme'),
        ('restaurant', 'Restaurateur (Legacy)'),
        ('driver', 'Livreur (Legacy)'),
    ]

    CITY_CHOICES = [
        ('Douala', 'Douala'),
        ('Yaoundé', 'Yaoundé'),
        ('Kribi', 'Kribi'),
        ('Bafoussam', 'Bafoussam'),
        ('Garoua', 'Garoua'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Rôle utilisateur"
    )
    must_change_password = models.BooleanField(
        default=False,
        verbose_name="Doit changer de mot de passe à la première connexion"
    )
    wallet_balance = models.PositiveIntegerField(
        default=0,
        verbose_name="Solde portefeuille simulé (FCFA)",
        help_text="Solde de démonstration de 10 000 FCFA offert à l'inscription"
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Numéro de téléphone",
        help_text="Ex: +237 699 00 11 22 ou 677 33 44 55"
    )
    city = models.CharField(
        max_length=50,
        choices=CITY_CHOICES,
        default='Douala',
        verbose_name="Ville principale"
    )
    neighborhood = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Quartier",
        help_text="Ex: Akwa, Bonapriso, Bastos, Omnisports, Deido"
    )
    address_details = models.TextField(
        blank=True,
        verbose_name="Précisions d'adresse / Repère",
        help_text="Ex: Rue des Palmiers, face pharmacie de l'Aéroport, barrière noire"
    )
    latitude = models.FloatField(null=True, blank=True, verbose_name="Latitude")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Longitude")
    avatar = models.URLField(
        blank=True,
        default='',
        verbose_name="Photo de profil (URL)"
    )
    is_verified = models.BooleanField(
        default=True,
        verbose_name="Compte vérifié"
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        full_name = self.get_full_name()
        name = full_name if full_name else self.username
        return f"{name} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_staff = True
            if self.role == 'client':
                self.role = 'admin'
        if self.role == 'admin':
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_client(self):
        return self.role == 'client'

    @property
    def is_restaurant(self):
        return self.role in ['restaurant', 'restaurateur']

    @property
    def is_driver(self):
        return self.role in ['driver', 'livreur']

    @property
    def is_platform_admin(self):
        return self.role == 'admin' or self.is_superuser

    def can_pay_with_wallet(self, amount):
        return self.wallet_balance >= amount

    def debit_wallet(self, amount):
        if not self.can_pay_with_wallet(amount):
            return False
        self.wallet_balance -= amount
        self.save(update_fields=['wallet_balance'])
        return True

    def credit_wallet(self, amount):
        self.wallet_balance += amount
        self.save(update_fields=['wallet_balance'])
        return True


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def grant_welcome_bonus(sender, instance, created, **kwargs):
    """
    Bonus de bienvenue simulé (solde de test) :
    À l'inscription, chaque nouveau client reçoit automatiquement un solde fictif
    de 10 000 F CFA, uniquement à des fins de simulation/démonstration.
    """
    if created and instance.role == 'client':
        if instance.wallet_balance == 0:
            CustomUser.objects.filter(pk=instance.pk).update(wallet_balance=10000)
            instance.wallet_balance = 10000

