from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'w-full bg-[#FFFFFF] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm'}),
            'comment': forms.Textarea(attrs={'class': 'w-full bg-[#FFFFFF] border border-[#E5DCD0] rounded-md px-3 py-2 text-sm', 'rows': 3, 'placeholder': 'Partagez vos impressions sur la cuisson, les assaisonnements, le goût du terroir...'}),
        }
