from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'city', 'phone', 'is_verified', 'is_staff')
    list_filter = ('role', 'city', 'is_verified', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Cameroun & Rôles', {
            'fields': ('role', 'phone', 'city', 'neighborhood', 'address_details', 'latitude', 'longitude', 'avatar', 'is_verified')
        }),
    )
