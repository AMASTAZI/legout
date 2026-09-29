import random
from django.db import models
from django.conf import settings
from django.utils import timezone
from restaurants.models import Restaurant, Dish

class Order(models.Model):
    STATUS_CHOICES = [
        ('en_attente_paiement', 'En attente de paiement'),
        ('payee', 'Payée - En attente de validation restaurant'),
        ('en_attente', 'En attente de validation'),
        ('validee', 'Validée par le restaurant'),
        ('confirmee', 'Confirmée par le restaurant'),
        ('en_preparation', 'En cours de préparation en cuisine'),
        ('prete', 'Prête / En attente du livreur'),
        ('en_livraison', 'En cours d\'acheminement'),
        ('livree', 'Livrée au client'),
        ('refusee', 'Refusée par le restaurant'),
        ('annulee', 'Annulée'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('wallet', 'Solde Portefeuille Simulé (10 000 FCFA Offerts)'),
        ('mtn_momo', 'MTN Mobile Money (*126#)'),
        ('orange_money', 'Orange Money (*150#)'),
        ('cinetpay', 'CinetPay (Passerelle sécurisée / Carte)'),
        ('cash_on_delivery', 'Paiement en espèces à la livraison'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('failed', 'Échec'),
        ('refunded', 'Remboursé'),
    ]

    order_number = models.CharField(max_length=40, unique=True, verbose_name="N° de commande")
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Client"
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Restaurant"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='en_attente',
        verbose_name="Statut de la commande"
    )
    subtotal = models.PositiveIntegerField(default=0, verbose_name="Sous-total plats (FCFA)")
    delivery_fee = models.PositiveIntegerField(default=1000, verbose_name="Frais de livraison (FCFA)")
    total_amount = models.PositiveIntegerField(default=0, verbose_name="Total à payer (FCFA)")
    
    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default='mtn_momo',
        verbose_name="Mode de règlement"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name="État du paiement"
    )

    DELIVERY_TYPE_CHOICES = [
        ('delivery', 'Livraison à domicile'),
        ('pickup', 'À emporter / Retrait au restaurant'),
    ]

    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPE_CHOICES,
        default='delivery',
        verbose_name="Mode de réception"
    )

    # Coordonnées réelles de livraison
    delivery_city = models.CharField(max_length=50, default='Douala', verbose_name="Ville de livraison")
    delivery_neighborhood = models.CharField(max_length=120, blank=True, default='', verbose_name="Quartier de livraison")
    delivery_address = models.CharField(max_length=255, blank=True, default='', verbose_name="Adresse / Rue")
    delivery_landmark = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Repère de proximité",
        help_text="Ex: Face pharmacie de la Paix, à côté du grand manguier"
    )
    delivery_phone = models.CharField(max_length=30, verbose_name="Numéro de contact pour livraison")
    client_notes = models.TextField(blank=True, verbose_name="Consignes spéciales de dégustation ou de livraison")

    # Code secret de sécurité (donné au livreur à l'arrivée pour finaliser)
    delivery_pin = models.CharField(max_length=4, default='1234', verbose_name="Code PIN de confirmation")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de commande")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.restaurant_id:
            restaurant = Restaurant.get_solo()
            if restaurant:
                self.restaurant = restaurant
        if not self.order_number:
            now_str = timezone.now().strftime("%y%m%d")
            rand_code = random.randint(1000, 9999)
            self.order_number = f"RG-{now_str}-{rand_code}"
        if not self.delivery_pin or self.delivery_pin == '1234':
            self.delivery_pin = str(random.randint(1000, 9999))
        if self.delivery_type == 'pickup':
            self.delivery_fee = 0
        self.total_amount = self.subtotal + self.delivery_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.client.get_full_name() or self.client.username} ({self.get_status_display()})"

    @property
    def can_be_cancelled(self):
        return self.status in ['en_attente_paiement', 'payee', 'en_attente', 'validee', 'confirmee']

    @property
    def progress_percentage(self):
        steps = {
            'en_attente_paiement': 5,
            'payee': 15,
            'en_attente': 15,
            'validee': 30,
            'confirmee': 30,
            'en_preparation': 55,
            'prete': 75,
            'en_livraison': 90,
            'livree': 100,
            'refusee': 0,
            'annulee': 0,
        }
        return steps.get(self.status, 15)

    def validate_order(self, target_status='validee'):
        """
        Action du restaurateur : valide la commande.
        La commande passe en 'validee' (ou 'confirmee') puis est transmise au livreur (ou mise à dispo).
        Le client et les livreurs reçoivent une notification.
        """
        self.status = target_status
        self.save(update_fields=['status', 'updated_at'])

        # Notification client
        Notification.objects.create(
            recipient=self.client,
            order=self,
            title="Commande validée par le restaurant !",
            message=f"Votre commande #{self.order_number} a été validée avec succès et passe en préparation en cuisine.",
            notif_type='order_validated'
        )

        # Si livraison à domicile : notification aux livreurs
        if self.delivery_type == 'delivery':
            from django.contrib.auth import get_user_model
            User = get_user_model()
            drivers = User.objects.filter(role__in=['livreur', 'driver'], is_active=True)
            for d in drivers:
                Notification.objects.create(
                    recipient=d,
                    order=self,
                    title="Nouvelle livraison à effectuer",
                    message=f"Course disponible pour la commande #{self.order_number} ({self.delivery_neighborhood}).",
                    notif_type='delivery_assigned'
                )

    def refuse_order(self, reason="Plat indisponible en cuisine"):
        """
        Action du restaurateur : refuse la commande.
        - Statut passe à 'refusee'
        - Remboursement automatique immédiat (solde portefeuille recrédité si payé par solde)
        - Notification de refus et remboursement au client
        - Facture mise à jour avec statut remboursé
        """
        self.status = 'refusee'

        if self.payment_status == 'paid':
            if self.payment_method == 'wallet':
                self.client.credit_wallet(self.total_amount)
            self.payment_status = 'refunded'

            # Traçabilité dans PaymentTransaction
            from payments.models import PaymentTransaction
            PaymentTransaction.objects.create(
                order=self,
                provider=self.payment_method if self.payment_method != 'cash_on_delivery' else 'cash',
                phone_number=self.delivery_phone or self.client.phone or '',
                amount=self.total_amount,
                status='successful',
                reference_code=f"REFUND-{self.order_number}"
            )

        self.save(update_fields=['status', 'payment_status', 'updated_at'])

        # Mise à jour facture
        if hasattr(self, 'invoice'):
            self.invoice.is_refunded = True
            self.invoice.save(update_fields=['is_refunded', 'updated_at'])

        # Course livreur annulée si existante
        if hasattr(self, 'delivery_mission'):
            self.delivery_mission.status = 'echec'
            self.delivery_mission.save(update_fields=['status'])

        # Notification client
        refund_info = f" Le montant de {self.total_amount} FCFA vous a été intégralement remboursé." if self.payment_status == 'refunded' else ""
        Notification.objects.create(
            recipient=self.client,
            order=self,
            title="Commande refusée & remboursée",
            message=f"Votre commande #{self.order_number} a été refusée par le restaurant ({reason}).{refund_info}",
            notif_type='order_rejected'
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Commande")
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name='order_items', verbose_name="Plat commandé")
    dish_name = models.CharField(max_length=150, verbose_name="Nom du plat")
    unit_price = models.PositiveIntegerField(verbose_name="Prix unitaire (FCFA)")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    subtotal = models.PositiveIntegerField(verbose_name="Sous-total (FCFA)")
    selected_side = models.CharField(max_length=150, blank=True, verbose_name="Accompagnement sélectionné")
    special_instructions = models.CharField(max_length=255, blank=True, verbose_name="Remarques (ex: bien pimenté, sauce à part)")

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"

    def save(self, *args, **kwargs):
        if not self.dish_name and self.dish:
            self.dish_name = self.dish.name
        if not self.unit_price and self.dish:
            self.unit_price = self.dish.price
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.dish_name} ({self.subtotal} FCFA)"


class Notification(models.Model):
    """
    Système de notifications en temps réel pour le client, le restaurateur et les livreurs.
    """
    NOTIF_TYPES = [
        ('order_created', 'Nouvelle commande'),
        ('order_validated', 'Commande validée par le restaurateur'),
        ('order_rejected', 'Commande refusée & Remboursée'),
        ('order_ready', 'Commande prête'),
        ('delivery_assigned', 'Nouvelle livraison disponible'),
        ('delivery_dispatched', 'Commande en cours de livraison'),
        ('order_delivered', 'Commande livrée'),
        ('refund', 'Remboursement'),
        ('info', 'Information'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Destinataire"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name="Commande associée"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    notif_type = models.CharField(
        max_length=30,
        choices=NOTIF_TYPES,
        default='info',
        verbose_name="Type de notification"
    )
    is_read = models.BooleanField(default=False, verbose_name="Lue")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date & Heure")

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_notif_type_display()}] {self.recipient.username} - {self.title}"


class Invoice(models.Model):
    """
    Facture / Reçu officiel généré automatiquement dès qu'un paiement est validé.
    Lié en OneToOneField à Order.
    Contient tous les détails : client, adresse/retrait, lignes, totaux, statut remboursé.
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='invoice',
        verbose_name="Commande associée"
    )
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="N° de facture / Reçu"
    )
    client_name = models.CharField(max_length=150, verbose_name="Nom complet du client")
    client_phone = models.CharField(max_length=40, verbose_name="Téléphone client")
    delivery_type = models.CharField(max_length=30, verbose_name="Mode de réception")
    delivery_address = models.CharField(max_length=255, verbose_name="Lieu de livraison ou retrait")
    subtotal = models.PositiveIntegerField(verbose_name="Sous-total plats (FCFA)")
    delivery_fee = models.PositiveIntegerField(default=0, verbose_name="Frais de livraison (FCFA)")
    total_amount = models.PositiveIntegerField(verbose_name="Total payé (FCFA)")
    payment_method = models.CharField(max_length=60, verbose_name="Mode de règlement")
    is_refunded = models.BooleanField(default=False, verbose_name="Statut remboursé")
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'émission")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Facture / Reçu"
        verbose_name_plural = "Factures / Reçus"
        ordering = ['-issued_at']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            now_str = timezone.now().strftime("%Y%m%d")
            rand_suffix = random.randint(1000, 9999)
            self.invoice_number = f"FAC-{now_str}-{rand_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        status_suffix = " (REMBOURSÉ)" if self.is_refunded else ""
        return f"Facture {self.invoice_number} - {self.client_name}{status_suffix}"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def order_invoice_handler(sender, instance, created, **kwargs):
    """
    Déclencheur automatique de génération ou mise à jour de la facture :
    - Dès que le paiement est 'paid', génération automatique du reçu/facture.
    - Si le paiement passe à 'refunded' ou la commande à 'refusee', mise à jour automatique.
    """
    if instance.payment_status == 'paid' and not hasattr(instance, 'invoice'):
        loc = instance.delivery_address
        if instance.delivery_type == 'pickup':
            loc = "À emporter / Retrait au restaurant"
        elif instance.delivery_neighborhood:
            loc = f"{instance.delivery_address}, {instance.delivery_neighborhood}"
            if instance.delivery_landmark:
                loc += f" ({instance.delivery_landmark})"

        client_name = instance.client.get_full_name() or instance.client.username
        Invoice.objects.create(
            order=instance,
            client_name=client_name,
            client_phone=instance.delivery_phone or instance.client.phone or '',
            delivery_type=instance.delivery_type,
            delivery_address=loc,
            subtotal=instance.subtotal,
            delivery_fee=instance.delivery_fee,
            total_amount=instance.total_amount,
            payment_method=instance.get_payment_method_display(),
            is_refunded=(instance.payment_status == 'refunded' or instance.status == 'refusee'),
        )
    elif hasattr(instance, 'invoice'):
        if instance.payment_status == 'refunded' or instance.status == 'refusee':
            if not instance.invoice.is_refunded:
                instance.invoice.is_refunded = True
                instance.invoice.save(update_fields=['is_refunded', 'updated_at'])

