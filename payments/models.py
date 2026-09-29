import uuid
from django.db import models
from orders.models import Order

class PaymentTransaction(models.Model):
    PROVIDER_CHOICES = [
        ('mtn_momo', 'MTN Mobile Money'),
        ('orange_money', 'Orange Money Cameroun'),
        ('cinetpay', 'CinetPay Gateway'),
        ('cash', 'Paiement à la livraison (Cash)'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En cours d\'autorisation'),
        ('successful', 'Paiement validé avec succès'),
        ('failed', 'Transaction refusée ou interrompue'),
        ('cancelled', 'Transaction annulée par l\'utilisateur'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Commande"
    )
    transaction_id = models.CharField(
        max_length=60,
        unique=True,
        verbose_name="Identifiant unique de transaction"
    )
    provider = models.CharField(
        max_length=30,
        choices=PROVIDER_CHOICES,
        default='mtn_momo',
        verbose_name="Opérateur de paiement"
    )
    phone_number = models.CharField(
        max_length=30,
        verbose_name="Numéro de compte débité",
        help_text="Ex: 677... (MTN) ou 690... (Orange)"
    )
    amount = models.PositiveIntegerField(verbose_name="Montant débité (FCFA)")
    currency = models.CharField(max_length=10, default="XAF", verbose_name="Devise")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut du paiement"
    )
    reference_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Code de référence opérateur / Token"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date & Heure")

    class Meta:
        verbose_name = "Transaction de paiement"
        verbose_name_plural = "Transactions de paiement"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TX-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} ({self.get_provider_display()}) - {self.amount} {self.currency} [{self.get_status_display()}]"
