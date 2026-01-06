from django.contrib import admin
from .models import MysteryContent, Review


@admin.register(MysteryContent)
class MysteryContentAdmin(admin.ModelAdmin):
    list_display = ["title", "content_type", "release_year", "average_quality"]
    list_filter = ["content_type", "release_year"]
    search_fields = ["title"]

    @admin.display(description="Avg Quality")
    def average_quality(self, obj):
        # Calculate an aggregate on the fly for the admin list
        from django.db.models import Avg

        result = obj.reviews.aggregate(Avg("overall_quality"))
        return (
            round(result["overall_quality__avg"], 1)
            if result["overall_quality__avg"]
            else "-"
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "content",
        "user",
        "overall_quality",
        "difficulty",
        "is_fair_play",
        "created_at",
    ]
    list_filter = ["is_fair_play", "difficulty", "overall_quality"]
    autocomplete_fields = ["content", "user"]
