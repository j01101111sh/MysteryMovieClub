from typing import Any

from django import template
from django.db.models import Count

from movies.models import MysteryTitle

register = template.Library()


@register.simple_tag
def get_review_heatmap(movie: MysteryTitle) -> dict[str, Any]:
    data = movie.reviews.values("quality", "difficulty").annotate(count=Count("id"))
    counts = {(d["quality"], d["difficulty"]): d["count"] for d in data}

    max_count = max(counts.values()) if counts else 0

    rows = []
    # Difficulty 5 down to 1
    for difficulty in range(5, 0, -1):
        cells = []
        # Quality 1 to 5
        for quality in range(1, 6):
            count = counts.get((quality, difficulty), 0)
            intensity = (count / max_count) if max_count > 0 else 0
            cells.append(
                {
                    "quality": quality,
                    "difficulty": difficulty,
                    "count": count,
                    "intensity": intensity,
                }
            )
        rows.append({"difficulty": difficulty, "cells": cells})

    return {"rows": rows, "max_count": max_count}
