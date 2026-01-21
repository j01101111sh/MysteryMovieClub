from typing import Any

from django.views.generic.base import ContextMixin


class ElidedPaginationMixin(ContextMixin):
    """
    Adds elided page range (e.g. 1 ... 4 5 6 ... 10) to the context.
    """

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if context.get("is_paginated") and context.get("paginator"):
            page_obj = context["page_obj"]
            context["elided_page_range"] = context["paginator"].get_elided_page_range(
                page_obj.number,
                on_each_side=2,
                on_ends=1,
            )
        return context
