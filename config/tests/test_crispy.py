"""
Unit tests for checking the integration and functionality of django-crispy-forms.
"""

import logging

from django import forms
from django.template import Context, Template
from django.test import TestCase

from movies.forms import CollectionForm, ReviewForm

# Configure logger for this module
logger = logging.getLogger(__name__)


class CrispyFormsTest(TestCase):
    """
    Test suite to verify that django-crispy-forms is correctly installed and configured.
    """

    def test_crispy_tag_loads(self) -> None:
        """
        Test that the crispy_forms_tags template library can be loaded without error.
        """
        template_string = "{% load crispy_forms_tags %}"
        try:
            Template(template_string)
        except Exception as e:
            self.fail(f"Failed to load crispy_forms_tags: {e}")

    def _assert_form_renders_crispy(
        self,
        form_class: type[forms.BaseForm],
        expected_fields: list[str],
    ) -> None:
        """Helper to test that a given form class renders with the crispy filter."""
        form = form_class()

        # We render the form using a raw template string to isolate the crispy functionality
        template_string = "{% load crispy_forms_tags %}{{ form|crispy }}"

        try:
            template = Template(template_string)
            context = Context({"form": form})
            rendered_html = template.render(context)

            logger.debug(
                "Rendered Crispy Form HTML for %s: %s",
                form_class.__name__,
                rendered_html,
            )

            # Assertions to ensure content was actually rendered
            self.assertTrue(
                rendered_html.strip(),
                f"The rendered HTML for {form_class.__name__} should not be empty.",
            )

            # Check for the presence of the form fields in the HTML
            for field in expected_fields:
                self.assertIn(f'name="{field}"', rendered_html)

            # Check for generic structural elements that indicate Crispy is doing its job
            self.assertIn("<div", rendered_html)

        except Exception as e:
            # If this fails with TemplateDoesNotExist, it usually means the CRISPY_TEMPLATE_PACK
            # setting is missing or the corresponding package (e.g., crispy-bootstrap5) is not installed.
            logger.error(
                "Crispy forms rendering failed for %s. Check CRISPY_TEMPLATE_PACK setting.",
                form_class.__name__,
            )
            self.fail(
                f"Crispy forms for {form_class.__name__} failed to render. "
                f"Likely configuration issue: {e}",
            )

    def test_review_form_renders_with_crispy(self) -> None:
        """
        Test that a ModelForm (ReviewForm) renders correctly using the |crispy filter.

        This test checks:
        1. The form instantiates correctly.
        2. The |crispy filter renders the form into HTML.
        3. The output contains expected HTML elements (verifying the template pack is active).
        """
        self._assert_form_renders_crispy(ReviewForm, ["quality", "comment"])

    def test_collection_form_renders_with_crispy(self) -> None:
        """
        Test that a ModelForm (CollectionForm) renders correctly using the |crispy filter.

        This test checks:
        1. The form instantiates correctly.
        2. The |crispy filter renders the form into HTML.
        3. The output contains expected HTML elements (verifying the template pack is active).
        """
        self._assert_form_renders_crispy(CollectionForm, ["name", "description"])
