from django.contrib import admin
from .models import Category, Restaurant, Dish

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'neighborhood', 'phone', 'price_range', 'rating', 'is_open', 'is_approved')
    list_filter = ('city', 'price_range', 'is_open', 'is_approved')
    search_fields = ('name', 'neighborhood', 'address')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'spice_level', 'authentic_origin', 'is_available', 'is_featured')
    list_filter = ('restaurant', 'category', 'spice_level', 'authentic_origin', 'is_available', 'is_featured')
    search_fields = ('name', 'description')
