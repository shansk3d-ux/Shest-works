from django.core.management import call_command
from django.test import TestCase

from apps.equipment.models import Brand, EquipmentType


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
