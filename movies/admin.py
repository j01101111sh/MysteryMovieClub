from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import (
    Collection,
    CollectionItem,
    Director,
    MysteryTitle,
    Review,
    ReviewHelpfulVote,
    Series,
    Tag,
    TagVote,
    WatchListEntry,
)


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MysteryTitle)
class MysteryTitleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "release_year",
        "media_type",
        "avg_quality",
        "avg_difficulty",
    ]
    list_filter = ["media_type", "release_year", "is_fair_play_candidate"]
    search_fields = ["title", "director__name"]
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (None, {"fields": ("title", "slug", "media_type", "release_year", "director")}),
        ("Synopsis", {"fields": ("description",)}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["movie", "user", "quality", "difficulty", "created_at"]
    list_filter = ["quality", "is_fair_play", "solved"]


@admin.register(ReviewHelpfulVote)
class ReviewHelpfulVoteAdmin(admin.ModelAdmin):
    """Admin interface for review helpful votes."""

    list_display = [
        "review",
        "user",
        "is_helpful",
        "created_at",
    ]
    list_filter = [
        "is_helpful",
        "created_at",
    ]
    search_fields = [
        "user__username",
        "review__movie__title",
        "review__user__username",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    date_hierarchy = "created_at"

    def get_queryset(self, request: HttpRequest) -> QuerySet[ReviewHelpfulVote]:
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related("user", "review", "review__user", "review__movie")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(TagVote)
class TagVoteAdmin(admin.ModelAdmin):
    list_display = ["movie", "tag", "user"]
    list_filter = ["tag", "movie"]


@admin.register(WatchListEntry)
class WatchListEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "added_at"]
    list_filter = ["user", "added_at"]
    search_fields = ["user__username", "movie__title"]


class CollectionItemInline(admin.TabularInline):
    model = CollectionItem
    extra = 1
    autocomplete_fields = ["movie"]


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "is_public", "updated_at"]
    list_filter = ["is_public", "created_at"]
    search_fields = ["name", "description", "user__username"]
    inlines = [CollectionItemInline]
