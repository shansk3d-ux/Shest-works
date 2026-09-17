from django.db import models

from apps.core.models import TimeStampedModel
from apps.equipment.models import Brand


class Part(TimeStampedModel):
    class Kind(models.TextChoices):
        PART = "part", "Запчасть"
        SERVICE = "service", "Услуга"

    name = models.CharField("Название", max_length=255)
    kind = models.CharField("Тип", max_length=10, choices=Kind.choices, default=Kind.PART)
    article = models.CharField("Артикул", max_length=100, blank=True)
    brand = models.ForeignKey(
        Brand,
        verbose_name="Бренд",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parts",
    )
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, default=0)
    notes = models.TextField("Заметки", blank=True)

    class Meta:
        verbose_name = "Запчасть или услуга"
        verbose_name_plural = "Запчасти и услуги"
        ordering = ["name"]

    def __str__(self):
        return self.name
