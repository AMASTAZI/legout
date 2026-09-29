from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from restaurants.models import Restaurant
from .models import Review
from .forms import ReviewForm

@login_required
def add_review(request, restaurant_slug):
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = restaurant
            review.client = request.user
            review.is_verified_purchase = True
            review.save()

            # Recalcul de la note moyenne
            all_reviews = restaurant.reviews.all()
            if all_reviews.exists():
                avg = sum(r.rating for r in all_reviews) / all_reviews.count()
                restaurant.rating = round(avg, 1)
                restaurant.total_reviews = all_reviews.count()
                restaurant.save()

            messages.success(request, "Votre avis a été publié avec succès. Merci de soutenir les restaurateurs locaux !")
        else:
            messages.error(request, "Impossible d'enregistrer l'avis. Vérifiez les champs.")

    return redirect('restaurants:detail', slug=restaurant.slug)
