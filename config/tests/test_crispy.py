"""
Unit tests for checking the integration and functionality of django-crispy-forms.
"""

import logging

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

    def test_review_form_renders_with_crispy(self) -> None:
        """
        Test that a ModelForm (ReviewForm) renders correctly using the |crispy filter.

        This test checks:
        1. The form instantiates correctly.
        2. The |crispy filter renders the form into HTML.
        3. The output contains expected HTML elements (verifying the template pack is active).
        """
        form = ReviewForm()

        # We render the form using a raw template string to isolate the crispy functionality
        template_string = "{% load crispy_forms_tags %}{{ form|crispy }}"

        try:
            template = Template(template_string)
            context = Context({"form": form})
            rendered_html = template.render(context)

            logger.debug("Rendered Crispy Form HTML: %s", rendered_html)

            # Assertions to ensure content was actually rendered
            self.assertTrue(
                rendered_html.strip(),
                "The rendered form HTML should not be empty.",
            )

            # Check for the presence of the form fields in the HTML
            self.assertIn('name="quality"', rendered_html)
            self.assertIn('name="comment"', rendered_html)

            # Check for generic structural elements that indicate Crispy is doing its job
            # (e.g., wrapping divs, though specific classes depend on the installed template pack)
            # If standard bootstrap pack is used, 'div' and 'class' attributes are expected.
            self.assertIn("<div", rendered_html)

        except Exception as e:
            # If this fails with TemplateDoesNotExist, it usually means the CRISPY_TEMPLATE_PACK
            # setting is missing or the corresponding package (e.g., crispy-bootstrap5) is not installed.
            logger.error(
                "Crispy forms rendering failed. Check CRISPY_TEMPLATE_PACK setting.",
            )
            self.fail(f"Crispy forms failed to render. likely configuration issue: {e}")

    def test_collection_form_renders_with_crispy(self) -> None:
        """
        Test that a ModelForm (CollectionForm) renders correctly using the |crispy filter.

        This test checks:
        1. The form instantiates correctly.
        2. The |crispy filter renders the form into HTML.
        3. The output contains expected HTML elements (verifying the template pack is active).
        """
        form = CollectionForm()

        # We render the form using a raw template string to isolate the crispy functionality
        template_string = "{% load crispy_forms_tags %}{{ form|crispy }}"

        try:
            template = Template(template_string)
            context = Context({"form": form})
            rendered_html = template.render(context)

            # Assertions to ensure content was actually rendered
            self.assertTrue(
                rendered_html.strip(),
                "The rendered form HTML should not be empty.",
            )

            # Check for the presence of the form fields in the HTML
            self.assertIn('name="name"', rendered_html)
            self.assertIn('name="description"', rendered_html)

            # Check for generic structural elements that indicate Crispy is doing its job
            # (e.g., wrapping divs, though specific classes depend on the installed template pack)
            # If standard bootstrap pack is used, 'div' and 'class' attributes are expected.
            self.assertIn("<div", rendered_html)

        except Exception as e:
            # If this fails with TemplateDoesNotExist, it usually means the CRISPY_TEMPLATE_PACK
            # setting is missing or the corresponding package (e.g., crispy-bootstrap5) is not installed.
            logger.error(
                "Crispy forms rendering failed. Check CRISPY_TEMPLATE_PACK setting.",
            )
            self.fail(f"Crispy forms failed to render. likely configuration issue: {e}")
