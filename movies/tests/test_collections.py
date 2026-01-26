from django.test import TestCase
from django.urls import reverse

from movies.models import Collection, CollectionItem
from movies.tests.factories import MovieFactory, UserFactory


class CollectionTests(TestCase):
    def setUp(self) -> None:
        self.user, self.upass = UserFactory.create()
        self.uname = self.user.get_username()
        self.movie = MovieFactory.create()
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
        otheruser, other_upass = UserFactory.create()
        other_uname = otheruser.get_username()

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

        otheruser, other_upass = UserFactory.create()
        other_uname = otheruser.get_username()

        self.client.login(username=other_uname, password=other_upass)

        response = self.client.post(
            reverse("movies:collection_remove_item", kwargs={"pk": item.pk}),
        )

        # UserPassesTestMixin returns 403 Forbidden
        self.assertEqual(response.status_code, 403)
        self.assertTrue(CollectionItem.objects.filter(pk=item.pk).exists())

    def test_my_collections_separation(self) -> None:
        """Test that the user's collections are separated from others."""
        # Create another user's public collection
        otheruser, _ = UserFactory.create()
        Collection.objects.create(
            name="Other's Favorites",
            user=otheruser,
            is_public=True,
        )

        self.client.login(username=self.uname, password=self.upass)
        response = self.client.get(reverse("movies:collection_list"))

        # Check that both collections are present
        self.assertContains(response, "My Favorites")
        self.assertContains(response, "Community Collections")

        # Verify context separation
        self.assertIn("my_collections", response.context)
        self.assertEqual(response.context["my_collections"].count(), 1)
        self.assertEqual(response.context["my_collections"][0], self.collection)

        # The main 'collections' list should NOT contain the user's collection
        self.assertNotIn(self.collection, response.context["collections"])
        self.assertEqual(response.context["collections"].count(), 1)

    def test_edit_collection_item_note(self) -> None:
        """Test that the owner can edit the note on a collection item."""
        item = CollectionItem.objects.create(
            collection=self.collection,
            movie=self.movie,
            note="Original note",
        )
        self.client.login(username=self.uname, password=self.upass)

        # Access the edit page
        url = reverse("movies:collection_item_edit", kwargs={"pk": item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Submit the change
        response = self.client.post(url, {"note": "Updated note"})
        self.assertRedirects(response, self.collection.get_absolute_url())

        # Verify the change
        item.refresh_from_db()
        self.assertEqual(item.note, "Updated note")

    def test_edit_item_permission(self) -> None:
        """Test that a non-owner cannot edit a collection item."""
        item = CollectionItem.objects.create(
            collection=self.collection,
            movie=self.movie,
        )

        # Create another user
        otheruser, other_upass = UserFactory.create()
        other_uname = otheruser.get_username()
        self.client.login(username=other_uname, password=other_upass)

        url = reverse("movies:collection_item_edit", kwargs={"pk": item.pk})
        response = self.client.post(url, {"note": "Hacked note"})

        self.assertEqual(response.status_code, 403)
        item.refresh_from_db()
        self.assertNotEqual(item.note, "Hacked note")
