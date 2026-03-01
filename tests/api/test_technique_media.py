from django.db import IntegrityError
from django.db.models.signals import post_save
from django.test import Client, TestCase

from files.models import Media, Technique, TechniqueMedia, media_save
from files.tests import create_account


class TestTechniqueMediaAPI(TestCase):
    fixtures = ["fixtures/categories.json", "fixtures/encoding_profiles.json"]

    def setUp(self):
        self.superuser = create_account(username="admin", is_superuser=True)
        self.regular_user = create_account(username="regular")

        # Disconnect the post_save signal to avoid needing a real media file
        post_save.disconnect(media_save, sender=Media)
        self.media = Media.objects.create(
            title="Test Video",
            friendly_token="testvideo123",
            user=self.superuser,
            media_type="video",
        )
        post_save.connect(media_save, sender=Media)

        # Create Technique objects in DB (guard → slx → slx-control)
        self.guard = Technique.objects.create(title="Guard", slug="root.guard", parent=None)
        self.slx = Technique.objects.create(title="SLX", slug="root.guard.slx", parent=self.guard)
        self.slx_control = Technique.objects.create(title="Slx Control", slug="root.guard.slx.slx-control", parent=self.slx)
        Technique.objects.rebuild()

        self.technique_id = "root.guard.slx.slx-control"

    def test_add_media_requires_auth(self):
        client = Client()
        url = f"/api/v1/techniques/{self.technique_id}/media"
        response = client.post(url, {"media_friendly_token": self.media.friendly_token}, content_type="application/json")
        # Anonymous users get redirected to login (302) or denied (403)
        self.assertIn(response.status_code, [302, 403])

    def test_add_media_requires_superuser(self):
        client = Client()
        client.force_login(self.regular_user)
        url = f"/api/v1/techniques/{self.technique_id}/media"
        response = client.post(url, {"media_friendly_token": self.media.friendly_token}, content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_add_media_success(self):
        client = Client()
        client.force_login(self.superuser)
        url = f"/api/v1/techniques/{self.technique_id}/media"
        response = client.post(url, {"media_friendly_token": self.media.friendly_token}, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(TechniqueMedia.objects.filter(technique=self.slx_control, media=self.media).exists())

    def test_add_media_duplicate_returns_409(self):
        TechniqueMedia.objects.create(technique=self.slx_control, media=self.media, added_by=self.superuser)
        client = Client()
        client.force_login(self.superuser)
        url = f"/api/v1/techniques/{self.technique_id}/media"
        response = client.post(url, {"media_friendly_token": self.media.friendly_token}, content_type="application/json")
        self.assertEqual(response.status_code, 409)

    def test_add_media_missing_token(self):
        client = Client()
        client.force_login(self.superuser)
        url = f"/api/v1/techniques/{self.technique_id}/media"
        response = client.post(url, {}, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_add_media_invalid_token(self):
        client = Client()
        client.force_login(self.superuser)
        url = f"/api/v1/techniques/{self.technique_id}/media"
        response = client.post(url, {"media_friendly_token": "nonexistent999"}, content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_remove_media_success(self):
        TechniqueMedia.objects.create(technique=self.slx_control, media=self.media, added_by=self.superuser)
        client = Client()
        client.force_login(self.superuser)
        url = f"/api/v1/techniques/{self.technique_id}/media/{self.media.friendly_token}"
        response = client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(TechniqueMedia.objects.filter(technique=self.slx_control, media=self.media).exists())

    def test_remove_media_not_found(self):
        client = Client()
        client.force_login(self.superuser)
        url = f"/api/v1/techniques/{self.technique_id}/media/{self.media.friendly_token}"
        response = client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_remove_media_requires_superuser(self):
        TechniqueMedia.objects.create(technique=self.slx_control, media=self.media, added_by=self.superuser)
        client = Client()
        client.force_login(self.regular_user)
        url = f"/api/v1/techniques/{self.technique_id}/media/{self.media.friendly_token}"
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_techniques_list_merges_media(self):
        TechniqueMedia.objects.create(technique=self.slx_control, media=self.media, added_by=self.superuser)
        client = Client()
        client.force_login(self.superuser)
        response = client.get("/api/v1/techniques")
        self.assertEqual(response.status_code, 200)
        tree = response.data.get("tree", [])
        found = self._find_node(tree, self.technique_id)
        self.assertIsNotNone(found, f"Node {self.technique_id} not found in tree")
        self.assertEqual(len(found["media"]), 1)
        self.assertEqual(found["media"][0]["friendly_token"], self.media.friendly_token)

    def test_technique_tree_requires_superuser(self):
        client = Client()
        client.force_login(self.regular_user)
        response = client.get("/api/v1/techniques/tree")
        self.assertEqual(response.status_code, 403)

    def test_technique_tree_success(self):
        client = Client()
        client.force_login(self.superuser)
        response = client.get("/api/v1/techniques/tree")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) > 0)
        node = response.data[0]
        self.assertIn("id", node)
        self.assertIn("title", node)

    def test_unique_constraint_at_db_level(self):
        TechniqueMedia.objects.create(technique=self.slx_control, media=self.media, added_by=self.superuser)
        with self.assertRaises(IntegrityError):
            TechniqueMedia.objects.create(technique=self.slx_control, media=self.media, added_by=self.superuser)

    def _find_node(self, nodes, target_id):
        for node in nodes:
            if node.get("id") == target_id:
                return node
            children = node.get("children", [])
            found = self._find_node(children, target_id)
            if found:
                return found
        return None
