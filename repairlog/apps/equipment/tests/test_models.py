from django.db import IntegrityError
from django.test import TestCase

from apps.clients.models import Client
from apps.equipment.models import Brand, Equipment, EquipmentType


class EquipmentModelTests(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(name="Кафе Уют")
        self.equipment_type = EquipmentType.objects.create(
            name="Пароконвектомат", category=EquipmentType.Category.KITCHEN
        )
        self.brand = Brand.objects.create(name="Rational")

    def test_str_combines_type_brand_model(self):
        equipment = Equipment.objects.create(
            client=self.client_obj,
            equipment_type=self.equipment_type,
            brand=self.brand,
            model="SCC 61",
            serial_number="SN-001",
        )
        self.assertEqual(str(equipment), "Пароконвектомат Rational SCC 61")

    def test_equipment_is_not_archived_by_default(self):
        equipment = Equipment.objects.create(
            client=self.client_obj,
            equipment_type=self.equipment_type,
            brand=self.brand,
            model="SCC 61",
        )
        self.assertFalse(equipment.is_archived)

    def test_brand_name_is_unique(self):
        Brand.objects.create(name="Unox")
        with self.assertRaises(IntegrityError):
            Brand.objects.create(name="Unox")
