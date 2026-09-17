from django.db import models

from apps.clients.models import Client
from apps.core.models import TimeStampedModel


class EquipmentType(TimeStampedModel):
    class Category(models.TextChoices):
        HOUSEHOLD = "household", "Бытовое"
        KITCHEN = "kitchen", "Кухонное"
        RESTAURANT = "restaurant", "Ресторанное"
        INDUSTRIAL = "industrial", "Промышленное"

    name = models.CharField("Название", max_length=255)
    category = models.CharField("Категория", max_length=20, choices=Category.choices)

    class Meta:
        verbose_name = "Тип оборудования"
        verbose_name_plural = "Типы оборудования"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Brand(TimeStampedModel):
    name = models.CharField("Название", max_length=255, unique=True)
    typical_equipment_types = models.ManyToManyField(
        EquipmentType,
        verbose_name="Характерные типы оборудования",
        related_name="typical_brands",
        blank=True,
    )

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Equipment(TimeStampedModel):
    client = models.ForeignKey(
        Client,
        verbose_name="Клиент",
        on_delete=models.CASCADE,
        related_name="equipment",
    )
    equipment_type = models.ForeignKey(
        EquipmentType,
        verbose_name="Тип оборудования",
        on_delete=models.PROTECT,
        related_name="equipment",
    )
    brand = models.ForeignKey(
        Brand,
        verbose_name="Бренд",
        on_delete=models.PROTECT,
        related_name="equipment",
    )
    model = models.CharField("Модель", max_length=255)
    serial_number = models.CharField(
        "Серийный номер", max_length=255, blank=True, db_index=True
    )
    year = models.PositiveSmallIntegerField("Год выпуска", null=True, blank=True)
    location = models.CharField("Место установки", max_length=255, blank=True)
    notes = models.TextField("Заметки", blank=True)
    is_archived = models.BooleanField("В архиве", default=False)

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.equipment_type} {self.brand} {self.model}".strip()
