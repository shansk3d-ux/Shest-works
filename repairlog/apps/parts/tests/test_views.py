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


class PartViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")
        self.client.force_login(self.user)
        self.brand = Brand.objects.create(name="Bosch")
        self.part = Part.objects.create(
            name="Тэн 2000W", article="TEN-2000", brand=self.brand, price=Decimal("1500.00")
        )


class PartListViewTests(PartViewsTestCase):
    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("parts:list"))
        self.assertEqual(response.status_code, 302)

    def test_lists_parts(self):
        response = self.client.get(reverse("parts:list"))
        self.assertContains(response, "Тэн 2000W")

    def test_search_by_article(self):
        Part.objects.create(name="Фильтр", article="FLT-1", price=Decimal("300.00"))
        response = self.client.get(reverse("parts:list"), {"q": "TEN-2000"})
        self.assertContains(response, "Тэн 2000W")
        self.assertNotContains(response, "Фильтр")

    def test_filter_by_kind(self):
        Part.objects.create(
            name="Диагностика", kind=Part.Kind.SERVICE, price=Decimal("500.00")
        )
        response = self.client.get(reverse("parts:list"), {"kind": Part.Kind.SERVICE})
        self.assertContains(response, "Диагностика")
        self.assertNotContains(response, "Тэн 2000W")


class PartDetailViewTests(PartViewsTestCase):
    def test_shows_part_info(self):
        response = self.client.get(reverse("parts:detail", args=[self.part.pk]))
        self.assertContains(response, "Тэн 2000W")
        self.assertContains(response, "TEN-2000")

    def test_shows_repairs_using_this_part(self):
        client_obj = Client.objects.create(name="Ресторан Восток")
        equipment_type = EquipmentType.objects.create(
            name="Пароконвектомат", category=EquipmentType.Category.KITCHEN
        )
        equipment = Equipment.objects.create(
            client=client_obj, equipment_type=equipment_type, brand=self.brand, model="SCC 61"
        )
        repair = Repair.objects.create(
            equipment=equipment,
            master=self.user,
            reported_at=timezone.localdate(),
            symptom="Не греет",
        )
        RepairPart.objects.create(
            repair=repair, part=self.part, quantity=1, price_at_use=self.part.price
        )
        response = self.client.get(reverse("parts:detail", args=[self.part.pk]))
        self.assertContains(response, f"Заявка №{repair.pk}")


class PartCreateViewTests(PartViewsTestCase):
    def test_creates_part_and_redirects_to_detail(self):
        response = self.client.post(
            reverse("parts:create"),
            {
                "name": "Насос",
                "kind": Part.Kind.PART,
                "article": "",
                "price": "2500.00",
                "notes": "",
            },
        )
        part = Part.objects.get(name="Насос")
        self.assertRedirects(response, reverse("parts:detail", args=[part.pk]))
        self.assertEqual(part.kind, Part.Kind.PART)

    def test_creates_a_service(self):
        response = self.client.post(
            reverse("parts:create"),
            {
                "name": "Диагностика",
                "kind": Part.Kind.SERVICE,
                "article": "",
                "price": "500.00",
                "notes": "",
            },
        )
        part = Part.objects.get(name="Диагностика")
        self.assertRedirects(response, reverse("parts:detail", args=[part.pk]))
        self.assertEqual(part.kind, Part.Kind.SERVICE)


class PartDeleteViewTests(PartViewsTestCase):
    def test_deletes_unused_part(self):
        response = self.client.post(reverse("parts:delete", args=[self.part.pk]))
        self.assertRedirects(response, reverse("parts:list"))
        self.assertFalse(Part.objects.filter(pk=self.part.pk).exists())

    def test_refuses_to_delete_part_used_in_a_repair(self):
        client_obj = Client.objects.create(name="Ресторан Восток")
        equipment_type = EquipmentType.objects.create(
            name="Пароконвектомат", category=EquipmentType.Category.KITCHEN
        )
        equipment = Equipment.objects.create(
            client=client_obj, equipment_type=equipment_type, brand=self.brand, model="SCC 61"
        )
        repair = Repair.objects.create(
            equipment=equipment,
            master=self.user,
            reported_at=timezone.localdate(),
            symptom="Не греет",
        )
        RepairPart.objects.create(
            repair=repair, part=self.part, quantity=1, price_at_use=self.part.price
        )
        response = self.client.post(reverse("parts:delete", args=[self.part.pk]))
        self.assertRedirects(response, reverse("parts:detail", args=[self.part.pk]))
        self.assertTrue(Part.objects.filter(pk=self.part.pk).exists())
