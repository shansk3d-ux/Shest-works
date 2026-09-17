from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.clients.models import Client
from apps.equipment.models import Brand, Equipment, EquipmentType
from apps.knowledge.models import Fault
from apps.repairs.models import Repair

User = get_user_model()


class GlobalSearchViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")
        self.client.force_login(self.user)

        client_obj = Client.objects.create(name="Ресторан Восток")
        equipment_type = EquipmentType.objects.create(
            name="Пароконвектомат", category=EquipmentType.Category.KITCHEN
        )
        brand = Brand.objects.create(name="Rational")
        self.equipment = Equipment.objects.create(
            client=client_obj, equipment_type=equipment_type, brand=brand, model="SCC 61"
        )
        self.repair = Repair.objects.create(
            equipment=self.equipment,
            master=self.user,
            reported_at=timezone.localdate(),
            symptom="Не морозит холодильная камера",
            diagnosis="Утечка фреона",
            error_code="E4",
        )
        self.fault = Fault.objects.create(
            equipment_type=equipment_type,
            brand=brand,
            error_code="E4",
            symptom="Не набирает температуру",
            cause="Забит фильтр подачи воды",
            solution="Прочистить фильтр и перезапустить цикл",
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 302)

    def test_empty_query_shows_prompt_without_results(self):
        response = self.client.get(reverse("search"))
        self.assertContains(response, "Введите запрос")
        self.assertEqual(list(response.context["repairs"]), [])
        self.assertEqual(list(response.context["faults"]), [])

    def test_finds_repair_by_symptom_text_with_stemming(self):
        response = self.client.get(reverse("search"), {"q": "морозить"})
        self.assertContains(response, "Не морозит холодильная камера")

    def test_finds_repair_by_diagnosis_text(self):
        response = self.client.get(reverse("search"), {"q": "фреон"})
        self.assertContains(response, "Не морозит холодильная камера")

    def test_finds_fault_by_solution_text(self):
        response = self.client.get(reverse("search"), {"q": "прочистить"})
        self.assertContains(response, "Забит фильтр подачи воды")

    def test_finds_by_error_code(self):
        response = self.client.get(reverse("search"), {"q": "E4"})
        self.assertContains(response, "Не морозит холодильная камера")
        self.assertContains(response, "Забит фильтр подачи воды")

    def test_no_match_shows_empty_state(self):
        response = self.client.get(reverse("search"), {"q": "несуществующийтекст"})
        self.assertContains(response, "Ничего не найдено")

    def test_archived_repair_is_still_searchable(self):
        self.repair.is_archived = True
        self.repair.save(update_fields=["is_archived"])
        response = self.client.get(reverse("search"), {"q": "морозить"})
        self.assertContains(response, "Не морозит холодильная камера")
