from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.equipment.models import Brand, Equipment, EquipmentType
from apps.parts.models import Part
from apps.repairs.models import Repair, RepairPart

User = get_user_model()


class RepairModelTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user(username="master", password="pass12345")
        client = Client.objects.create(name="Ресторан Восток")
        equipment_type = EquipmentType.objects.create(
            name="Холодильный шкаф", category=EquipmentType.Category.RESTAURANT
        )
        brand = Brand.objects.create(name="Electrolux")
        self.equipment = Equipment.objects.create(
            client=client, equipment_type=equipment_type, brand=brand, model="RE401"
        )

    def test_default_status_is_new(self):
        repair = Repair.objects.create(
            equipment=self.equipment,
            master=self.master,
            reported_at=timezone.now().date(),
            symptom="Не морозит",
        )
        self.assertEqual(repair.status, Repair.Status.NEW)

    def test_repair_is_not_archived_by_default(self):
        repair = Repair.objects.create(
            equipment=self.equipment,
            master=self.master,
            reported_at=timezone.now().date(),
            symptom="Не морозит",
        )
        self.assertFalse(repair.is_archived)

    def test_total_cost_sums_labor_and_parts(self):
        repair = Repair.objects.create(
            equipment=self.equipment,
            master=self.master,
            reported_at=timezone.now().date(),
            symptom="Не морозит",
            labor_cost=Decimal("1500.00"),
            parts_cost=Decimal("750.50"),
        )
        self.assertEqual(repair.total_cost, Decimal("2250.50"))

    def test_str_contains_repair_id(self):
        repair = Repair.objects.create(
            equipment=self.equipment,
            master=self.master,
            reported_at=timezone.now().date(),
            symptom="Не морозит",
        )
        self.assertIn(str(repair.pk), str(repair))


class RepairPartModelTests(TestCase):
    def test_str_shows_part_and_quantity(self):
        master = User.objects.create_user(username="master2", password="pass12345")
        client = Client.objects.create(name="Кафе Плюс")
        equipment_type = EquipmentType.objects.create(
            name="Стиральная машина", category=EquipmentType.Category.HOUSEHOLD
        )
        brand = Brand.objects.create(name="Bosch")
        equipment = Equipment.objects.create(
            client=client, equipment_type=equipment_type, brand=brand, model="WAT28"
        )
        repair = Repair.objects.create(
            equipment=equipment,
            master=master,
            reported_at=timezone.now().date(),
            symptom="Не сливает воду",
        )
        part = Part.objects.create(name="Насос слива", price=Decimal("1200.00"))
        repair_part = RepairPart.objects.create(
            repair=repair, part=part, quantity=2, price_at_use=Decimal("1200.00")
        )
        self.assertEqual(str(repair_part), "Насос слива × 2")
