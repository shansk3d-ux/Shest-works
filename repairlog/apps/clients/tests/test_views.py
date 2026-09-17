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

    def test_offers_call_and_max_buttons_when_phone_is_set(self):
        response = self.client.get(reverse("clients:detail", args=[self.client_obj.pk]))
        self.assertContains(response, 'href="tel:+79990001122"')
        self.assertContains(response, "write-max-btn")
        self.assertContains(response, 'data-phone="+79990001122"')
        self.assertNotContains(response, "no-phone-btn")

    def test_offers_no_phone_redirect_when_phone_is_missing(self):
        client_without_phone = Client.objects.create(name="Кафе Без Номера")
        response = self.client.get(reverse("clients:detail", args=[client_without_phone.pk]))
        self.assertContains(response, "no-phone-btn")
        self.assertContains(
            response,
            f'data-edit-url="{reverse("clients:update", args=[client_without_phone.pk])}"',
        )
        self.assertNotContains(response, "write-max-btn")


class ClientInnTests(ClientViewsTestCase):
    def test_detail_shows_inn_when_set(self):
        self.client_obj.inn = "770708389431"
        self.client_obj.save(update_fields=["inn"])
        response = self.client.get(reverse("clients:detail", args=[self.client_obj.pk]))
        self.assertContains(response, "770708389431")
        self.assertContains(response, 'data-inn="770708389431"')

    def test_detail_offers_nalog_button_without_inn_to_copy(self):
        response = self.client.get(reverse("clients:detail", args=[self.client_obj.pk]))
        self.assertContains(response, "nalog-btn")
        self.assertNotContains(response, "data-inn=")

    def test_saves_inn_from_the_form(self):
        self.client.post(
            reverse("clients:update", args=[self.client_obj.pk]),
            {
                "name": self.client_obj.name,
                "client_type": Client.ClientType.ORGANIZATION,
                "inn": "7707083893",
            },
        )
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.inn, "7707083893")

    def test_rejects_an_inn_that_is_not_10_or_12_digits(self):
        response = self.client.post(
            reverse("clients:update", args=[self.client_obj.pk]),
            {
                "name": self.client_obj.name,
                "client_type": Client.ClientType.ORGANIZATION,
                "inn": "12345",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.inn, "")


class ClientCreateViewTests(ClientViewsTestCase):
    def test_creates_client_and_redirects_to_detail(self):
        response = self.client.post(
            reverse("clients:create"),
            {"name": "Новый клиент", "client_type": Client.ClientType.INDIVIDUAL},
        )
        client = Client.objects.get(name="Новый клиент")
        self.assertRedirects(response, reverse("clients:detail", args=[client.pk]))

    def test_offers_contact_import_button(self):
        response = self.client.get(reverse("clients:create"))
        self.assertContains(response, "import-contact-btn")
        self.assertContains(response, "navigator.contacts")


class ClientUpdateViewTests(ClientViewsTestCase):
    def test_updates_client(self):
        response = self.client.post(
            reverse("clients:update", args=[self.client_obj.pk]),
            {"name": "Ресторан Запад", "client_type": Client.ClientType.ORGANIZATION},
        )
        self.assertRedirects(response, reverse("clients:detail", args=[self.client_obj.pk]))
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.name, "Ресторан Запад")

    def test_does_not_offer_contact_import_button(self):
        response = self.client.get(reverse("clients:update", args=[self.client_obj.pk]))
        self.assertNotContains(response, "import-contact-btn")


class ClientDeleteViewTests(ClientViewsTestCase):
    def test_deletes_client(self):
        response = self.client.post(reverse("clients:delete", args=[self.client_obj.pk]))
        self.assertRedirects(response, reverse("clients:list"))
        self.assertFalse(Client.objects.filter(pk=self.client_obj.pk).exists())
