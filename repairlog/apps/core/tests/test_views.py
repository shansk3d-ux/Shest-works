from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    def test_home_page_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_contains_project_name(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "RepairLog")
