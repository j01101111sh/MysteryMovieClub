from django.contrib import admin

from .models import Director, MysteryTitle, Review, Series, Tag, TagVote, WatchListEntry


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
