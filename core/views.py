from django.shortcuts import render
from restaurants.models import Restaurant, Dish
from reviews.models import Review

def home(request):
    """
    Page vitrine publique de l'unique restaurant (mono-restaurant).
    Accessible à tout le monde sans compte.
    Présentation du restaurant, horaires, zone de livraison,
    menu complet avec prix (plats, entrées, boissons du terroir, desserts) et avis certifiés.
    """
    restaurant = Restaurant.get_solo()

    # Recherche directe dans la carte du restaurant
    query = request.GET.get('q', '').strip()

    base_dishes = Dish.objects.filter(is_available=True).select_related('category')
    if query:
        base_dishes = base_dishes.filter(name__icontains=query)

    # Répartition des produits de la carte (avec section boissons séparée)
    main_dishes = base_dishes.filter(product_type='plat')
    starters = base_dishes.filter(product_type='entree')
    drinks = base_dishes.filter(product_type='boisson')
    desserts = base_dishes.filter(product_type='dessert')
    featured_dishes = base_dishes.filter(is_featured=True)[:4]

    # Avis vérifiés sur les commandes
    recent_reviews = Review.objects.filter(is_verified_purchase=True).select_related('client')[:6]

    context = {
        'restaurant': restaurant,
        'main_dishes': main_dishes,
        'starters': starters,
        'drinks': drinks,
        'desserts': desserts,
        'featured_dishes': featured_dishes,
        'recent_reviews': recent_reviews,
        'search_query': query,
    }
    return render(request, 'core/home.html', context)


def cgu(request):
    """Conditions Générales d'Utilisation et de Vente"""
    restaurant = Restaurant.get_solo()
    return render(request, 'core/cgu.html', {'restaurant': restaurant})


def privacy(request):
    """Politique de Confidentialité et Protection des Données Personnelles"""
    restaurant = Restaurant.get_solo()
    return render(request, 'core/privacy.html', {'restaurant': restaurant})
