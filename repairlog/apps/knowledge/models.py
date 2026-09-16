from django.db import models

from apps.core.models import TimeStampedModel
from apps.equipment.models import Brand, EquipmentType


class Fault(TimeStampedModel):
    equipment_type = models.ForeignKey(
        EquipmentType,
        verbose_name="Тип оборудования",
        on_delete=models.CASCADE,
        related_name="faults",
    )
    brand = models.ForeignKey(
        Brand,
        verbose_name="Бренд",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faults",
    )
    model_pattern = models.CharField("Модель / маска модели", max_length=255, blank=True)
    error_code = models.CharField("Код ошибки", max_length=50, blank=True, db_index=True)
    symptom = models.TextField("Симптом")
    cause = models.TextField("Причина")
    solution = models.TextField("Решение")

    class Meta:
        verbose_name = "Типовая неисправность"
        verbose_name_plural = "База знаний: неисправности"
        ordering = ["equipment_type__name", "error_code"]

    def __str__(self):
        return f"{self.equipment_type}: {self.error_code or self.symptom[:40]}"
