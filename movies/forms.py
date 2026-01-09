from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["quality", "difficulty", "is_fair_play", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4}),
        }
