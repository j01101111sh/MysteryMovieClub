import secrets

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from movies.models import Collection, CollectionItem, MysteryTitle


class CollectionTests(TestCase):
    def setUp(self) -> None:
        self.uname = f"user_{secrets.token_hex(4)}"
        self.upass = secrets.token_urlsafe(16)

        self.user = get_user_model().objects.create_user(  # type: ignore
            username=self.uname,
            password=self.upass,
        )
        self.movie = MysteryTitle.objects.create(
            title="Knives Out",
            release_year=2019,
            slug="knives-out",
        )
        self.collection = Collection.objects.create(
            name="My Favorites",
            user=self.user,
            is_public=True,
        )

    def test_collection_creation(self) -> None:
        """Test that a collection can be created correctly."""
        self.assertEqual(self.collection.name, "My Favorites")
        self.assertEqual(self.collection.user, self.user)

    def test_add_item_to_collection(self) -> None:
        """Test adding a movie to a collection."""
        item = CollectionItem.objects.create(
            collection=self.collection,
            movie=self.movie,
            note="Great movie!",
        )
        self.assertEqual(self.collection.items.count(), 1)
        self.assertEqual(item.note, "Great movie!")

    def test_collection_list_view(self) -> None:
        """Test the collection list view."""
        response = self.client.get(reverse("movies:collection_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Favorites")

    def test_collection_detail_view(self) -> None:
        """Test the collection detail view."""
        response = self.client.get(self.collection.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Favorites")

    def test_private_collection_access(self) -> None:
        """Test that private collections are not visible to others."""
        self.collection.is_public = False
        self.collection.save()

        # Logout
        self.client.logout()

        response = self.client.get(self.collection.get_absolute_url())
        self.assertEqual(response.status_code, 404)

        # Login as owner
        self.client.login(username=self.uname, password=self.upass)
        response = self.client.get(self.collection.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_delete_collection(self) -> None:
        """Test that the owner can delete their collection."""
        self.client.login(username=self.uname, password=self.upass)
        initial_count = Collection.objects.count()

        response = self.client.post(
            reverse("movies:collection_delete", kwargs={"pk": self.collection.pk}),
        )

        self.assertRedirects(response, reverse("movies:collection_list"))
        self.assertEqual(Collection.objects.count(), initial_count - 1)
        self.assertFalse(
            Collection.objects.filter(pk=self.collection.pk).exists(),
        )

    def test_delete_collection_permission(self) -> None:
        """Test that a user cannot delete a collection they do not own."""
        other_uname = f"user_{secrets.token_hex(4)}"
        other_upass = secrets.token_urlsafe(16)
        get_user_model().objects.create_user(  # type: ignore
            username=other_uname,
            password=other_upass,
        )

        self.client.login(username=other_uname, password=other_upass)

        # Attempt to delete the original user's collection
        response = self.client.post(
            reverse("movies:collection_delete", kwargs={"pk": self.collection.pk}),
        )

        # UserPassesTestMixin returns 403 Forbidden
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Collection.objects.filter(pk=self.collection.pk).exists(),
        )

    def test_remove_item_from_collection(self) -> None:
        """Test that the owner can remove an item from their collection."""
        item = CollectionItem.objects.create(
            collection=self.collection,
            movie=self.movie,
        )
        self.client.login(username=self.uname, password=self.upass)

        response = self.client.post(
            reverse("movies:collection_remove_item", kwargs={"pk": item.pk}),
        )

        self.assertRedirects(response, self.collection.get_absolute_url())
        self.assertFalse(CollectionItem.objects.filter(pk=item.pk).exists())

    def test_remove_item_permission(self) -> None:
        """Test that a user cannot remove an item from a collection they do not own."""
        item = CollectionItem.objects.create(
            collection=self.collection,
            movie=self.movie,
        )

        other_uname = f"user_{secrets.token_hex(4)}"
        other_upass = secrets.token_urlsafe(16)
        get_user_model().objects.create_user(  # type: ignore
            username=other_uname,
            password=other_upass,
        )

        self.client.login(username=other_uname, password=other_upass)

        response = self.client.post(
            reverse("movies:collection_remove_item", kwargs={"pk": item.pk}),
        )

        # UserPassesTestMixin returns 403 Forbidden
        self.assertEqual(response.status_code, 403)
        self.assertTrue(CollectionItem.objects.filter(pk=item.pk).exists())
