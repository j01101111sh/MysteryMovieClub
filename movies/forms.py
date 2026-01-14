from django import forms

from .models import Review, Tag


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["quality", "difficulty", "is_fair_play", "solved", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4}),
        }


class TagVoteForm(forms.Form):
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        empty_label="Select a tag...",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
