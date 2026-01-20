from django import forms

from .models import Collection, CollectionItem, Review, Tag


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


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ["name", "description", "is_public"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class CollectionAddItemForm(forms.ModelForm):
    class Meta:
        model = CollectionItem
        fields = ["note"]
        widgets = {
            "note": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Optional note..."},
            ),
        }
