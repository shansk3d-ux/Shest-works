from django.test import TestCase

from apps.clients.models import Client
from apps.clients.templatetags.client_extras import CLIENT_ICONS, client_icon


class ClientIconFilterTests(TestCase):
    def test_returns_a_path_into_the_client_icons_directory(self):
        client = Client.objects.create(name="Ресторан Восток")
        icon_path = client_icon(client)
        self.assertTrue(icon_path.startswith("images/client-icons/"))
        self.assertIn(icon_path.rsplit("/", 1)[-1], CLIENT_ICONS)

    def test_is_stable_for_the_same_client(self):
        client = Client.objects.create(name="Ресторан Восток")
        self.assertEqual(client_icon(client), client_icon(client))

    def test_can_differ_between_clients(self):
        clients = [Client.objects.create(name=f"Клиент {i}") for i in range(len(CLIENT_ICONS) + 1)]
        icons = {client_icon(client) for client in clients}
        self.assertGreater(len(icons), 1)
