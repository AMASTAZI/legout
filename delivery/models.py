from django.db import models
from django.conf import settings
from orders.models import Order

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('recherche_livreur', 'Recherche d\'un coursier à proximité'),
        ('assignee', 'Course acceptée par le livreur'),
        ('arrivee_restaurant', 'Livreur arrivé au restaurant'),
        ('recuperee', 'Colis chaud récupéré / En route'),
        ('arrivee_client', 'Livreur sur le pas de porte'),
        ('livree', 'Course terminée & confirmée'),
        ('echec', 'Échec ou annulation de livraison'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery_mission',
        verbose_name="Commande associée"
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries',
        verbose_name="Livreur assigné"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='recherche_livreur',
        verbose_name="Statut de la course"
    )
    driver_phone = models.CharField(max_length=30, blank=True, verbose_name="Contact direct du livreur")
    
    # Points géographiques
    pickup_address = models.CharField(max_length=255, blank=True, verbose_name="Adresse de départ (Restaurant)")
    pickup_latitude = models.FloatField(default=4.051056, verbose_name="Lat. Restaurant")
    pickup_longitude = models.FloatField(default=9.708535, verbose_name="Long. Restaurant")
    
    dropoff_address = models.CharField(max_length=255, blank=True, verbose_name="Adresse d'arrivée (Client)")
    dropoff_latitude = models.FloatField(default=4.048500, verbose_name="Lat. Client")
    dropoff_longitude = models.FloatField(default=9.698000, verbose_name="Long. Client")
    
    current_latitude = models.FloatField(default=4.050000, verbose_name="Lat. Actuelle Coursier")
    current_longitude = models.FloatField(default=9.705000, verbose_name="Long. Actuelle Coursier")

    distance_km = models.FloatField(default=3.8, verbose_name="Distance calculée (km)")
    estimated_duration_min = models.PositiveIntegerField(default=25, verbose_name="Durée estimée (minutes)")
    driver_payout = models.PositiveIntegerField(default=800, verbose_name="Gain net coursier (FCFA)")
    
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name="Heure de prise en charge")
    picked_up_at = models.DateTimeField(null=True, blank=True, verbose_name="Heure de départ restaurant")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Heure effective de remise")

    class Meta:
        verbose_name = "Course de livraison"
        verbose_name_plural = "Courses de livraison"
        ordering = ['-order__created_at']

    def __str__(self):
        driver_name = self.driver.get_full_name() if self.driver else "Non assigné"
        return f"Course #{self.order.order_number} - {driver_name} ({self.get_status_display()})"
