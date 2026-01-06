from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['overall_quality', 'difficulty', 'is_fair_play', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your thoughts on the mystery...'}),
            'is_fair_play': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }