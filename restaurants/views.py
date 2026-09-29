from django.shortcuts import render, redirect
from .models import Restaurant, Dish

def restaurant_list(request):
    """
    Dans l'architecture mono-restaurant, il n'y a plus de liste multi-restaurants.
    Redirige directement vers la page vitrine et le menu de l'établissement unique.
    """
    return redirect('core:home')

def restaurant_detail(request, slug=None):
    """Redirige vers l'accueil de l'établissement unique"""
    return redirect('core:home')
