from django.contrib import admin

from .models import MysteryTitle, Review


@admin.register(MysteryTitle)
class MysteryTitleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "release_year",
        "media_type",
        "avg_quality",
        "fair_play_consensus",
    )
    list_filter = ("media_type", "is_fair_play_candidate")
    search_fields = ("title", "director")
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (None, {"fields": ("title", "slug", "media_type", "release_year", "director")}),
        ("Synopsis", {"fields": ("description",)}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("movie__title", "user__username", "comment")
