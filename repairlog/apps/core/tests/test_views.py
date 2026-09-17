from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_authenticated_user_sees_home_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Опять работа?")


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_valid_login_redirects_to_home(self):
        response = self.client.post(
            reverse("login"), {"username": "master", "password": "pass12345"}
        )
        self.assertRedirects(response, reverse("home"))

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse("login"), {"username": "master", "password": "wrong-password"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))


class ClipboardHelperTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")

    def test_copy_helper_loads_before_the_scripts_that_call_it(self):
        self.client.force_login(self.user)
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn("js/clipboard.js", html)
        self.assertLess(html.index("js/clipboard.js"), html.index("js/phone-actions.js"))
        self.assertLess(html.index("js/clipboard.js"), html.index("js/nalog-actions.js"))
