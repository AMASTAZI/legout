from django import forms
from .models import Review
from restaurants.models import Dish

class ReviewForm(forms.ModelForm):
    dish = forms.ModelChoiceField(
        queryset=Dish.objects.filter(is_available=True).order_by('name'),
        required=False,
        empty_label="— Tous les plats / Expérience globale —",
        widget=forms.Select(attrs={
            'class': 'w-full bg-[#FFFFFF] border border-[#E5DCD0] rounded-md px-3 py-2 text-xs focus:outline-none focus:border-[#A83B19]'
        })
    )

    class Meta:
        model = Review
        fields = ['rating', 'dish', 'comment']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'w-full bg-[#FFFFFF] border border-[#E5DCD0] rounded-md px-3 py-2 text-xs font-semibold focus:outline-none focus:border-[#A83B19]'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full bg-[#FFFFFF] border border-[#E5DCD0] rounded-md px-3 py-2 text-xs focus:outline-none focus:border-[#A83B19]',
                'rows': 3,
                'placeholder': 'Partagez vos impressions sur la cuisson, les assaisonnements, la température et le goût authentique...'
            }),
        }
