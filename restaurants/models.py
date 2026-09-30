from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.URLField(blank=True, verbose_name="Image d'illustration (URL)")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Catégorie Culinaire"
        verbose_name_plural = "Catégories Culinaires"
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    """
    Modèle Singleton représentant l'unique établissement du site (mono-restaurant).
    Tous les plats, boissons, horaires et paramètres de livraison lui appartiennent.
    """
    PRICE_CHOICES = [
        ('$', 'Économique (< 2 000 FCFA)'),
        ('$$', 'Moyen (2 000 - 5 000 FCFA)'),
        ('$$$', 'Gastronomique (> 5 000 FCFA)'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_restaurant',
        verbose_name="Restaurateur / Gérant assigné"
    )
    name = models.CharField(max_length=150, default="Le Gout", verbose_name="Nom du restaurant")
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    tagline = models.CharField(max_length=200, blank=True, verbose_name="Slogan / Identité culinaire")
    description = models.TextField(verbose_name="Présentation authentique du restaurant")
    phone = models.CharField(max_length=30, verbose_name="Téléphone de contact & commandes")
    email = models.EmailField(blank=True, verbose_name="Email professionnel")
    city = models.CharField(max_length=50, default='Douala', verbose_name="Ville")
    neighborhood = models.CharField(max_length=120, default='Akwa', verbose_name="Quartier")
    address = models.CharField(max_length=255, verbose_name="Adresse physique & repères précis")
    latitude = models.FloatField(default=4.051056, verbose_name="Latitude GPS")
    longitude = models.FloatField(default=9.708535, verbose_name="Longitude GPS")
    cover_image = models.URLField(blank=True, verbose_name="Bannière principale (URL)")
    logo_image = models.URLField(blank=True, verbose_name="Logo du restaurant (URL)")
    categories = models.ManyToManyField(Category, blank=True, related_name='restaurants', verbose_name="Spécialités couvertes")
    price_range = models.CharField(max_length=5, choices=PRICE_CHOICES, default='$$', verbose_name="Gamme de prix")
    opening_time = models.TimeField(default="10:30", verbose_name="Heure d'ouverture")
    closing_time = models.TimeField(default="22:30", verbose_name="Heure de fermeture")
    is_open = models.BooleanField(default=True, verbose_name="Ouvert aux commandes actuellement")
    is_approved = models.BooleanField(default=True, verbose_name="Établissement actif")
    delivery_fee = models.PositiveIntegerField(default=1000, verbose_name="Frais de livraison forfaitaire (FCFA)")
    min_order_amount = models.PositiveIntegerField(default=2000, verbose_name="Montant minimum de commande (FCFA)")
    delivery_zone = models.CharField(
        max_length=255,
        default="Douala (Akwa, Bonapriso, Deido, Bonamoussadi, Bali, Bépanda, Makepe)",
        verbose_name="Zone de livraison couverte"
    )
    estimated_delivery_time = models.CharField(max_length=50, default="35 - 50 min", verbose_name="Délai estimé de livraison")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Note moyenne")
    total_reviews = models.PositiveIntegerField(default=0, verbose_name="Nombre d'avis")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Restaurant (Singleton)"
        verbose_name_plural = "Restaurant (Singleton)"

    @classmethod
    def get_solo(cls):
        """Retourne l'unique restaurant ou None s'il n'a pas encore été configuré"""
        return cls.objects.first()

    def save(self, *args, **kwargs):
        # Garantit qu'un seul enregistrement existe en base (modèle Singleton)
        if not self.pk and Restaurant.objects.exists():
            self.pk = Restaurant.objects.first().pk
        if not self.slug:
            self.slug = slugify(self.name) or "restaurant"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.neighborhood}, {self.city}"


class Dish(models.Model):
    SPICE_CHOICES = [
        ('doux', 'Doux (Sans piment piquant)'),
        ('moyen', 'Piment moyen (Rehaussé au pèbè & rondelles)'),
        ('releve', 'Relevé (Piment jaune du village)'),
        ('fort', 'Très fort (Piment oiseau camerounais pur)'),
    ]

    ORIGIN_CHOICES = [
        ('Littoral (Sawa)', 'Littoral / Terroir Sawa (Wouri, Moungo, Sanaga)'),
        ('Ouest (Bamiléké)', 'Ouest / Terroir Grassfields & Bamiléké'),
        ('Centre & Sud (Beti)', 'Centre, Sud & Est / Terroir Beti & Fang'),
        ('Nord (Sahel)', 'Grand Nord / Sahel (Soya, Kilichi, Boule)'),
        ('Sud-Ouest (Côte)', 'Sud-Ouest & Anglophone (Eru, Achu, Koki)'),
        ('Pan-Africain', 'Grillades & Boissons artisanales'),
    ]

    PRODUCT_TYPE_CHOICES = [
        ('plat', 'Plat principal du terroir'),
        ('boisson', 'Boisson & Rafraîchissement'),
        ('entree', 'Entrée / Amuse-bouche'),
        ('dessert', 'Dessert / Douceur'),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='dishes',
        null=True,
        blank=True,
        verbose_name="Restaurant"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dishes',
        verbose_name="Catégorie"
    )
    name = models.CharField(max_length=150, verbose_name="Nom du produit / plat")
    slug = models.SlugField(max_length=180, blank=True)
    description = models.TextField(verbose_name="Description détaillée des ingrédients et saveurs")
    price = models.PositiveIntegerField(verbose_name="Prix unitaire (FCFA)")
    image = models.CharField(max_length=500, blank=True, default='', verbose_name="Photo réelle du plat (URL ou chemin)")
    image_file = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name="Fichier photo téléversé")
    is_available = models.BooleanField(default=True, verbose_name="Disponible en cuisine")
    is_featured = models.BooleanField(default=False, verbose_name="Plat du Chef / Populaire")
    prep_time_minutes = models.PositiveIntegerField(default=25, verbose_name="Temps de préparation (min)")
    spice_level = models.CharField(max_length=20, choices=SPICE_CHOICES, default='moyen', verbose_name="Niveau d'épices")
    authentic_origin = models.CharField(max_length=60, choices=ORIGIN_CHOICES, default='Littoral (Sawa)', verbose_name="Origine régionale")
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='plat',
        verbose_name="Type de produit"
    )
    sides_included = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="Accompagnements inclus ou au choix"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_drink(self):
        return self.product_type == 'boisson'

    @property
    def categorie(self):
        return self.product_type

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg, 1) if avg else None
        return None

    @property
    def total_reviews_count(self):
        return self.reviews.count()

    def get_absolute_url(self):
        from django.urls import reverse
        if self.slug:
            return reverse('restaurants:dish_detail', kwargs={'slug': self.slug})
        return reverse('core:home')

    class Meta:
        verbose_name = "Produit / Plat"
        verbose_name_plural = "Produits & Plats"
        ordering = ['-is_featured', 'product_type', 'price', 'name']

    def save(self, *args, **kwargs):
        if not self.restaurant_id:
            restaurant = Restaurant.get_solo()
            if restaurant:
                self.restaurant = restaurant
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
        super().save(*args, **kwargs)
        if self.image_file:
            try:
                new_url = self.image_file.url
                if self.image != new_url:
                    self.image = new_url
                    Dish.objects.filter(pk=self.pk).update(image=new_url)
            except Exception:
                pass

    def __str__(self):
        return f"{self.name} - {self.price} FCFA ({self.get_product_type_display()})"


Product = Dish
