from django.test import TestCase

from apps.clients.models import Client


class ClientModelTests(TestCase):
    def test_str_returns_name(self):
        client = Client.objects.create(name="Ресторан Вкусно")
        self.assertEqual(str(client), "Ресторан Вкусно")

    def test_default_client_type_is_individual(self):
        client = Client.objects.create(name="Иван Иванов")
        self.assertEqual(client.client_type, Client.ClientType.INDIVIDUAL)
