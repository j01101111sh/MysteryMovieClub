from django.contrib import admin
from .models import MysteryTitle


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
        (
            "Mystery Metrics",
            {
                "fields": (
                    "is_fair_play_candidate",
                    "avg_quality",
                    "avg_difficulty",
                    "fair_play_consensus",
                )
            },
        ),
    )
