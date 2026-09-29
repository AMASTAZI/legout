from django.contrib import admin
from .models import Delivery

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'driver', 'status', 'distance_km', 'estimated_duration_min', 'driver_payout')
    list_filter = ('status',)
    search_fields = ('order__order_number', 'driver__username')
