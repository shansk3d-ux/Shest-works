from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.equipment.models import Brand, EquipmentType
from apps.knowledge.models import Fault
from apps.repairs.models import Repair

User = get_user_model()


class FaultSuggestionsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")
        self.client.force_login(self.user)
        self.equipment_type = EquipmentType.objects.create(
            name="Пароконвектомат", category=EquipmentType.Category.KITCHEN
        )
        self.other_type = EquipmentType.objects.create(
            name="Посудомоечная машина", category=EquipmentType.Category.KITCHEN
        )
        self.brand = Brand.objects.create(name="Rational")
        self.fault = Fault.objects.create(
            equipment_type=self.equipment_type,
            brand=self.brand,
            error_code="E4",
            symptom="Не набирает температуру",
            cause="Забит фильтр подачи воды",
            solution="Прочистить фильтр",
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("knowledge:fault_suggestions"))
        self.assertEqual(response.status_code, 302)

    def test_without_equipment_type_returns_nothing(self):
        response = self.client.get(reverse("knowledge:fault_suggestions"))
        self.assertEqual(list(response.context["faults"]), [])
        self.assertNotContains(response, "Похожих случаев")

    def test_matches_by_equipment_type(self):
        response = self.client.get(
            reverse("knowledge:fault_suggestions"), {"equipment_type": self.equipment_type.pk}
        )
        self.assertContains(response, "Не набирает температуру")

    def test_does_not_match_other_equipment_type(self):
        response = self.client.get(
            reverse("knowledge:fault_suggestions"), {"equipment_type": self.other_type.pk}
        )
        self.assertNotContains(response, "Не набирает температуру")
        self.assertContains(response, "не найдено")

    def test_filters_by_error_code(self):
        Fault.objects.create(
            equipment_type=self.equipment_type,
            error_code="E7",
            symptom="Другая неисправность",
            cause="...",
            solution="...",
        )
        response = self.client.get(
            reverse("knowledge:fault_suggestions"),
            {"equipment_type": self.equipment_type.pk, "error_code": "E4"},
        )
        self.assertContains(response, "Не набирает температуру")
        self.assertNotContains(response, "Другая неисправность")

    def test_orders_by_repairs_count_descending(self):
        from apps.clients.models import Client
        from apps.equipment.models import Equipment

        popular_fault = Fault.objects.create(
            equipment_type=self.equipment_type,
            error_code="E9",
            symptom="Частая поломка",
            cause="...",
            solution="...",
        )
        client = Client.objects.create(name="Клиент")
        equipment = Equipment.objects.create(
            client=client, equipment_type=self.equipment_type, brand=self.brand, model="M1"
        )
        import datetime

        for _ in range(3):
            Repair.objects.create(
                equipment=equipment,
                master=self.user,
                reported_at=datetime.date.today(),
                symptom="x",
                fault=popular_fault,
            )

        response = self.client.get(
            reverse("knowledge:fault_suggestions"), {"equipment_type": self.equipment_type.pk}
        )
        faults = list(response.context["faults"])
        self.assertEqual(faults[0], popular_fault)
