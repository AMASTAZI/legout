from django.db import models
from django.conf import settings
from restaurants.models import Restaurant, Dish
from orders.models import Order

class Review(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Restaurant noté"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_reviews',
        verbose_name="Auteur de l'avis"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name="Commande vérifiée"
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name="Plat spécifique (optionnel)"
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(1, '1 étoile - Très décevant'),
                 (2, '2 étoiles - Passable'),
                 (3, '3 étoiles - Bon'),
                 (4, '4 étoiles - Très bon'),
                 (5, '5 étoiles - Excellent terroir')],
        default=5,
        verbose_name="Note sur 5"
    )
    comment = models.TextField(verbose_name="Commentaire d'expérience culinaire")
    is_verified_purchase = models.BooleanField(default=True, verbose_name="Commande vérifiée")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Publié le")

    class Meta:
        verbose_name = "Avis client"
        verbose_name_plural = "Avis clients"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}/5 par {self.client.get_full_name() or self.client.username} sur {self.restaurant.name}"
