import json
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class ManifestTests(TestCase):
    def test_manifest_is_valid_json_with_required_fields(self):
        manifest_path = Path(settings.BASE_DIR) / "static" / "manifest.json"
        data = json.loads(manifest_path.read_text())

        self.assertEqual(data["name"], "Опять работа?")
        self.assertEqual(data["display"], "standalone")
        self.assertEqual(data["start_url"], "/")

        sizes = {icon["sizes"] for icon in data["icons"]}
        self.assertIn("192x192", sizes)
        self.assertIn("512x512", sizes)
        for icon in data["icons"]:
            icon_path = Path(settings.BASE_DIR) / icon["src"].lstrip("/")
            self.assertTrue(icon_path.exists(), f"missing icon file: {icon_path}")

    def test_referenced_icon_files_exist_on_disk(self):
        images_dir = Path(settings.BASE_DIR) / "static" / "images"
        for name in ("icon-192.png", "icon-512.png", "apple-touch-icon.png", "logo.png"):
            self.assertTrue((images_dir / name).exists(), f"missing {name}")


class ServiceWorkerViewTests(TestCase):
    def test_served_at_site_root_with_js_content_type(self):
        response = self.client.get("/service-worker.js")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/javascript")

    def test_url_name_resolves_to_root_path(self):
        self.assertEqual(reverse("service_worker"), "/service-worker.js")

    def test_registers_install_and_fetch_handlers(self):
        response = self.client.get("/service-worker.js")
        content = response.content.decode()
        self.assertIn('addEventListener("install"', content)
        self.assertIn('addEventListener("fetch"', content)

    def test_does_not_cache_non_static_requests(self):
        response = self.client.get("/service-worker.js")
        content = response.content.decode()
        self.assertIn('/static/', content)
