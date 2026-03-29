from django import forms
from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    review = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Write your review here'}))

    class Meta:
        model = ProductReview
        fields = ['rating', 'review']
