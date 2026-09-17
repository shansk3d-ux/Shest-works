from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.clients.models import Client
from apps.equipment.models import Brand, Equipment, EquipmentType
from apps.parts.models import Part
from apps.repairs.models import Repair, RepairPart

User = get_user_model()


class RepairPartViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")
        self.client.force_login(self.user)
        client_obj = Client.objects.create(name="Ресторан Восток")
        equipment_type = EquipmentType.objects.create(
            name="Пароконвектомат", category=EquipmentType.Category.KITCHEN
        )
        brand = Brand.objects.create(name="Rational")
        equipment = Equipment.objects.create(
            client=client_obj, equipment_type=equipment_type, brand=brand, model="SCC 61"
        )
        self.repair = Repair.objects.create(
            equipment=equipment,
            master=self.user,
            reported_at=timezone.localdate(),
            symptom="Течёт вода",
        )
        self.part = Part.objects.create(name="Тэн 2000W", price=Decimal("1500.00"))


class RepairPartAddViewTests(RepairPartViewsTestCase):
    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse("repairs:part_add", args=[self.repair.pk]))
        self.assertEqual(response.status_code, 302)

    def test_adds_part_with_price_snapshot(self):
        response = self.client.post(
            reverse("repairs:part_add", args=[self.repair.pk]),
            {"part": self.part.name, "quantity": 2},
        )
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        used_part = self.repair.used_parts.get()
        self.assertEqual(used_part.part, self.part)
        self.assertEqual(used_part.quantity, 2)
        self.assertEqual(used_part.price_at_use, self.part.price)

    def test_price_snapshot_survives_later_catalog_price_change(self):
        self.client.post(
            reverse("repairs:part_add", args=[self.repair.pk]),
            {"part": self.part.name, "quantity": 1},
        )
        self.part.price = Decimal("2000.00")
        self.part.save(update_fields=["price"])
        used_part = self.repair.used_parts.get()
        self.assertEqual(used_part.price_at_use, Decimal("1500.00"))

    def test_invalid_form_adds_nothing(self):
        response = self.client.post(
            reverse("repairs:part_add", args=[self.repair.pk]),
            {"part": self.part.name, "quantity": 0},
        )
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        self.assertEqual(self.repair.used_parts.count(), 0)

    def test_typing_a_new_part_creates_and_keeps_it(self):
        response = self.client.post(
            reverse("repairs:part_add", args=[self.repair.pk]),
            {
                "part": "__new__",
                "part_new_name": "Фильтр воды",
                "part_new_kind": Part.Kind.PART,
                "part_new_price": "450.00",
                "quantity": 1,
            },
        )
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        used_part = self.repair.used_parts.get()
        self.assertEqual(used_part.part.name, "Фильтр воды")
        self.assertEqual(used_part.part.kind, Part.Kind.PART)
        self.assertEqual(used_part.price_at_use, Decimal("450.00"))
        # It's now a real catalog entry, not just attached to this one repair.
        self.assertTrue(Part.objects.filter(name="Фильтр воды").exists())

    def test_typing_a_new_service_creates_and_keeps_it(self):
        response = self.client.post(
            reverse("repairs:part_add", args=[self.repair.pk]),
            {
                "part": "__new__",
                "part_new_name": "Диагностика",
                "part_new_kind": Part.Kind.SERVICE,
                "part_new_price": "600.00",
                "quantity": 1,
            },
        )
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        used_part = self.repair.used_parts.get()
        self.assertEqual(used_part.part.name, "Диагностика")
        self.assertEqual(used_part.part.kind, Part.Kind.SERVICE)

    def test_new_item_reuses_existing_one_case_insensitively(self):
        # Latin name here: SQLite's UPPER()/LOWER() (unlike Postgres's) only
        # case-folds ASCII, so a Cyrillic case-insensitive match would only
        # work against the real Postgres used in production.
        latin_part = Part.objects.create(name="Filter", price=Decimal("100.00"))
        response = self.client.post(
            reverse("repairs:part_add", args=[self.repair.pk]),
            {
                "part": "__new__",
                "part_new_name": latin_part.name.upper(),
                "part_new_price": "999.00",
                "quantity": 1,
            },
        )
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        used_part = self.repair.used_parts.get()
        self.assertEqual(used_part.part, latin_part)
        # The existing price is kept, not overwritten by the "new" price typed in.
        self.assertEqual(used_part.price_at_use, latin_part.price)
        self.assertEqual(Part.objects.filter(name__iexact=latin_part.name).count(), 1)

    def test_new_item_without_price_is_rejected(self):
        response = self.client.post(
            reverse("repairs:part_add", args=[self.repair.pk]),
            {"part": "__new__", "part_new_name": "Фильтр воды", "quantity": 1},
        )
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        self.assertEqual(self.repair.used_parts.count(), 0)
        self.assertFalse(Part.objects.filter(name="Фильтр воды").exists())


class RepairPartDeleteViewTests(RepairPartViewsTestCase):
    def setUp(self):
        super().setUp()
        self.used_part = RepairPart.objects.create(
            repair=self.repair, part=self.part, quantity=1, price_at_use=self.part.price
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse("repairs:part_delete", args=[self.used_part.pk]))
        self.assertEqual(response.status_code, 302)

    def test_deletes_used_part(self):
        response = self.client.post(reverse("repairs:part_delete", args=[self.used_part.pk]))
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        self.assertFalse(RepairPart.objects.filter(pk=self.used_part.pk).exists())


class RepairCatalogPartsCostTests(RepairPartViewsTestCase):
    def test_sums_quantity_times_price_at_use(self):
        RepairPart.objects.create(
            repair=self.repair, part=self.part, quantity=3, price_at_use=Decimal("100.00")
        )
        other_part = Part.objects.create(name="Фильтр", price=Decimal("50.00"))
        RepairPart.objects.create(
            repair=self.repair, part=other_part, quantity=2, price_at_use=Decimal("50.00")
        )
        self.assertEqual(self.repair.catalog_parts_cost, Decimal("400.00"))
