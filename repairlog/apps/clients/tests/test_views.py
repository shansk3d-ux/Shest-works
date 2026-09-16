from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.clients.models import Client

User = get_user_model()


class ClientViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")
        self.client.force_login(self.user)
        self.client_obj = Client.objects.create(name="Ресторан Восток", phone="+79990001122")


class ClientListViewTests(ClientViewsTestCase):
    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("clients:list"))
        self.assertEqual(response.status_code, 302)

    def test_lists_clients(self):
        response = self.client.get(reverse("clients:list"))
        self.assertContains(response, "Ресторан Восток")

    def test_search_by_name(self):
        Client.objects.create(name="Кафе Плюс")
        response = self.client.get(reverse("clients:list"), {"q": "Восток"})
        self.assertContains(response, "Ресторан Восток")
        self.assertNotContains(response, "Кафе Плюс")

    def test_search_by_phone(self):
        response = self.client.get(reverse("clients:list"), {"q": "9990001122"})
        self.assertContains(response, "Ресторан Восток")


class ClientDetailViewTests(ClientViewsTestCase):
    def test_shows_client_info(self):
        response = self.client.get(reverse("clients:detail", args=[self.client_obj.pk]))
        self.assertContains(response, "Ресторан Восток")
        self.assertContains(response, "+79990001122")


class ClientCreateViewTests(ClientViewsTestCase):
    def test_creates_client_and_redirects_to_detail(self):
        response = self.client.post(
            reverse("clients:create"),
            {"name": "Новый клиент", "client_type": Client.ClientType.INDIVIDUAL},
        )
        client = Client.objects.get(name="Новый клиент")
        self.assertRedirects(response, reverse("clients:detail", args=[client.pk]))


class ClientUpdateViewTests(ClientViewsTestCase):
    def test_updates_client(self):
        response = self.client.post(
            reverse("clients:update", args=[self.client_obj.pk]),
            {"name": "Ресторан Запад", "client_type": Client.ClientType.ORGANIZATION},
        )
        self.assertRedirects(response, reverse("clients:detail", args=[self.client_obj.pk]))
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.name, "Ресторан Запад")


class ClientDeleteViewTests(ClientViewsTestCase):
    def test_deletes_client(self):
        response = self.client.post(reverse("clients:delete", args=[self.client_obj.pk]))
        self.assertRedirects(response, reverse("clients:list"))
        self.assertFalse(Client.objects.filter(pk=self.client_obj.pk).exists())
