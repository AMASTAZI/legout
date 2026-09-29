from django import forms
from .models import Restaurant, Dish

class RestaurantForm(forms.ModelForm):
    """Formulaire de gestion des paramètres de l'unique établissement (Singleton)"""
    class Meta:
        model = Restaurant
        fields = [
            'name', 'tagline', 'description', 'phone', 'email',
            'city', 'neighborhood', 'address', 'opening_time', 'closing_time',
            'delivery_fee', 'min_order_amount', 'delivery_zone', 'is_open'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'tagline': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'city': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'neighborhood': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'address': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'opening_time': forms.TimeInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]', 'type': 'time'}),
            'delivery_fee': forms.NumberInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'min_order_amount': forms.NumberInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'delivery_zone': forms.TextInput(attrs={'class': 'w-full bg-[#FAF6F0] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#A83B19] text-[#221C18]'}),
            'is_open': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#A83B19] rounded'}),
        }
