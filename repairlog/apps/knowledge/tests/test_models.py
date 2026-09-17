from django.test import TestCase

from apps.equipment.models import EquipmentType
from apps.knowledge.models import Fault


class FaultModelTests(TestCase):
    def setUp(self):
        self.equipment_type = EquipmentType.objects.create(
            name="Посудомоечная машина", category=EquipmentType.Category.KITCHEN
        )

    def test_str_uses_error_code_when_present(self):
        fault = Fault.objects.create(
            equipment_type=self.equipment_type,
            error_code="E4",
            symptom="Не набирает воду",
            cause="Забит фильтр подачи воды",
            solution="Прочистить фильтр",
        )
        self.assertEqual(str(fault), "Посудомоечная машина: E4")

    def test_str_falls_back_to_symptom_without_error_code(self):
        fault = Fault.objects.create(
            equipment_type=self.equipment_type,
            symptom="Течёт вода из-под двери",
            cause="Изношен уплотнитель",
            solution="Заменить уплотнитель двери",
        )
        self.assertTrue(str(fault).endswith("Течёт вода из-под двери"))
