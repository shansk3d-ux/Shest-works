from decimal import Decimal

from django.test import TestCase

from apps.equipment.models import Brand
from apps.parts.models import Part


class PartModelTests(TestCase):
    def test_str_returns_name(self):
        part = Part.objects.create(name="Тэн 2000W", price=Decimal("1500.00"))
        self.assertEqual(str(part), "Тэн 2000W")

    def test_brand_is_optional(self):
        part = Part.objects.create(name="Фильтр", price=Decimal("300.00"))
        self.assertIsNone(part.brand)

    def test_part_can_have_brand(self):
        brand = Brand.objects.create(name="Bosch")
        part = Part.objects.create(name="Насос", brand=brand, price=Decimal("2500.00"))
        self.assertEqual(part.brand, brand)
