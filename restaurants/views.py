from django.shortcuts import render, redirect, get_object_or_404
from .models import Restaurant, Dish
from reviews.forms import ReviewForm

def restaurant_list(request):
    """
    Dans l'architecture mono-restaurant, il n'y a plus de liste multi-restaurants.
    Redirige directement vers la page vitrine et le menu de l'établissement unique.
    """
    return redirect('core:home')

def restaurant_detail(request, slug=None):
    """Redirige vers l'accueil de l'établissement unique"""
    return redirect('core:home')

def dish_detail(request, slug):
    """
    Fiche produit détaillée (Plat ou Boisson) :
    Affiche la photo, le nom, la description complète, le prix, la catégorie,
    la disponibilité, la note moyenne calculée sur ce produit, le nombre total d'avis,
    les avis clients spécifiques à ce produit, et l'ajout au panier avec sélecteur de quantité.
    """
    dish = get_object_or_404(Dish, slug=slug)
    restaurant = Restaurant.get_solo()
    reviews = dish.reviews.all().select_related('client').order_by('-created_at')
    
    total_reviews = reviews.count()
    if total_reviews > 0:
        avg_rating = round(sum(r.rating for r in reviews) / total_reviews, 1)
        stars_breakdown = []
        for star in [5, 4, 3, 2, 1]:
            count = reviews.filter(rating=star).count()
            pct = round((count / total_reviews) * 100)
            stars_breakdown.append({'star': star, 'count': count, 'pct': pct})
    else:
        avg_rating = None
        stars_breakdown = []

    related_dishes = Dish.objects.filter(
        product_type=dish.product_type,
        is_available=True
    ).exclude(pk=dish.pk)[:4]

    review_form = ReviewForm(initial={'dish': dish}) if request.user.is_authenticated else None

    context = {
        'dish': dish,
        'restaurant': restaurant,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'stars_breakdown': stars_breakdown,
        'related_dishes': related_dishes,
        'review_form': review_form,
    }
    return render(request, 'restaurants/dish_detail.html', context)

