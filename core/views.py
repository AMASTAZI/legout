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

    from django.core.paginator import Paginator

    # Répartition des produits de la carte (avec section boissons séparée)
    main_dishes_qs = base_dishes.filter(product_type='plat')
    drinks_qs = base_dishes.filter(product_type='boisson')
    starters = base_dishes.filter(product_type='entree')
    desserts = base_dishes.filter(product_type='dessert')
    featured_dishes = base_dishes.filter(is_featured=True)[:4]

    # Pagination : max 6 plats et 6 boissons par page
    dishes_paginator = Paginator(main_dishes_qs, 6)
    page_plats = request.GET.get('page_plats', 1)
    main_dishes = dishes_paginator.get_page(page_plats)

    drinks_paginator = Paginator(drinks_qs, 6)
    page_boissons = request.GET.get('page_boissons', 1)
    drinks = drinks_paginator.get_page(page_boissons)

    # Avis vérifiés et statistiques de notation
    if restaurant:
        reviews_qs = restaurant.reviews.all().select_related('client', 'dish').order_by('-created_at')
    else:
        reviews_qs = Review.objects.all().select_related('client', 'dish').order_by('-created_at')

    total_reviews_count = reviews_qs.count()
    if total_reviews_count > 0:
        avg_rating = round(sum(r.rating for r in reviews_qs) / total_reviews_count, 1)
        stars_breakdown = []
        for star in [5, 4, 3, 2, 1]:
            count = reviews_qs.filter(rating=star).count()
            pct = round((count / total_reviews_count) * 100)
            stars_breakdown.append({'star': star, 'count': count, 'pct': pct})
    else:
        avg_rating = float(restaurant.rating) if (restaurant and restaurant.rating) else 5.0
        stars_breakdown = [
            {'star': 5, 'count': 0, 'pct': 0},
            {'star': 4, 'count': 0, 'pct': 0},
            {'star': 3, 'count': 0, 'pct': 0},
            {'star': 2, 'count': 0, 'pct': 0},
            {'star': 1, 'count': 0, 'pct': 0},
        ]

    recent_reviews = reviews_qs[:10]
    review_dishes = Dish.objects.filter(is_available=True).order_by('name')

    context = {
        'restaurant': restaurant,
        'main_dishes': main_dishes,
        'starters': starters,
        'drinks': drinks,
        'desserts': desserts,
        'featured_dishes': featured_dishes,
        'recent_reviews': recent_reviews,
        'total_reviews_count': total_reviews_count,
        'avg_rating': avg_rating,
        'stars_breakdown': stars_breakdown,
        'review_dishes': review_dishes,
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
