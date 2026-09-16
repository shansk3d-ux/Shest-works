import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from apps.equipment.models import Brand, EquipmentType

User = get_user_model()


class SeedCommandTests(TestCase):
    def test_seed_creates_equipment_types_and_brands(self):
        call_command("seed")
        self.assertGreater(EquipmentType.objects.count(), 0)
        self.assertGreater(Brand.objects.count(), 0)
        self.assertTrue(Brand.objects.filter(name="Rational").exists())

    def test_seed_is_idempotent(self):
        call_command("seed")
        types_after_first_run = EquipmentType.objects.count()
        brands_after_first_run = Brand.objects.count()

        call_command("seed")

        self.assertEqual(EquipmentType.objects.count(), types_after_first_run)
        self.assertEqual(Brand.objects.count(), brands_after_first_run)

    def test_seed_covers_all_categories(self):
        call_command("seed")
        categories = set(EquipmentType.objects.values_list("category", flat=True))
        self.assertEqual(
            categories,
            {
                EquipmentType.Category.HOUSEHOLD,
                EquipmentType.Category.KITCHEN,
                EquipmentType.Category.RESTAURANT,
                EquipmentType.Category.INDUSTRIAL,
            },
        )


class BootstrapDemoCommandTests(TestCase):
    def test_creates_demo_superuser_and_seeds_data(self):
        call_command("bootstrap_demo")
        user = User.objects.get(username="demo")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("opyat-rabota-demo"))
        self.assertGreater(EquipmentType.objects.count(), 0)

    def test_uses_env_vars_for_credentials(self):
        with mock.patch.dict(
            os.environ, {"DEMO_USERNAME": "master", "DEMO_PASSWORD": "s3cr3t"}
        ):
            call_command("bootstrap_demo")
        user = User.objects.get(username="master")
        self.assertTrue(user.check_password("s3cr3t"))

    def test_is_idempotent_and_resets_password(self):
        call_command("bootstrap_demo")
        user = User.objects.get(username="demo")
        user.set_password("something-else")
        user.save()

        call_command("bootstrap_demo")

        self.assertEqual(User.objects.filter(username="demo").count(), 1)
        user.refresh_from_db()
        self.assertTrue(user.check_password("opyat-rabota-demo"))
