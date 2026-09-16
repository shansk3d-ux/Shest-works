from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.equipment.models import Equipment
from apps.knowledge.models import Fault
from apps.parts.models import Part


def repair_photo_upload_path(instance, filename):
    return f"repairs/{instance.repair_id}/{filename}"


class Repair(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        DIAGNOSTICS = "diagnostics", "Диагностика"
        AWAITING_PARTS = "awaiting_parts", "Ждём запчасти"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Выполнена"
        REJECTED = "rejected", "Отказ"

    equipment = models.ForeignKey(
        Equipment,
        verbose_name="Оборудование",
        on_delete=models.CASCADE,
        related_name="repairs",
    )
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Мастер",
        on_delete=models.PROTECT,
        related_name="repairs",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW
    )
    reported_at = models.DateField("Дата обращения")
    completed_at = models.DateField("Дата завершения", null=True, blank=True)
    symptom = models.TextField("Симптом (со слов клиента)")
    error_code = models.CharField("Код ошибки", max_length=50, blank=True, db_index=True)
    diagnosis = models.TextField("Диагноз", blank=True)
    work_done = models.TextField("Выполненные работы", blank=True)
    fault = models.ForeignKey(
        Fault,
        verbose_name="Типовая неисправность",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="repairs",
    )
    labor_cost = models.DecimalField(
        "Стоимость работ", max_digits=10, decimal_places=2, default=Decimal("0")
    )
    parts_cost = models.DecimalField(
        "Стоимость запчастей", max_digits=10, decimal_places=2, default=Decimal("0")
    )
    warranty_until = models.DateField("Гарантия до", null=True, blank=True)
    is_archived = models.BooleanField("В архиве", default=False)

    class Meta:
        verbose_name = "Ремонт"
        verbose_name_plural = "Ремонты"
        ordering = ["-reported_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["reported_at"]),
        ]

    def __str__(self):
        return f"Ремонт №{self.pk} — {self.equipment}"

    @property
    def total_cost(self):
        return self.labor_cost + self.parts_cost

    @property
    def catalog_parts_cost(self):
        return sum((used_part.subtotal for used_part in self.used_parts.all()), Decimal("0"))


class RepairPhoto(TimeStampedModel):
    class Stage(models.TextChoices):
        BEFORE = "before", "До"
        DURING = "during", "Во время"
        AFTER = "after", "После"

    repair = models.ForeignKey(
        Repair, verbose_name="Ремонт", on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField("Фото", upload_to=repair_photo_upload_path)
    caption = models.CharField("Подпись", max_length=255, blank=True)
    stage = models.CharField("Этап", max_length=10, choices=Stage.choices, default=Stage.BEFORE)

    class Meta:
        verbose_name = "Фото ремонта"
        verbose_name_plural = "Фото ремонта"
        ordering = ["created_at"]

    def __str__(self):
        return f"Фото ({self.get_stage_display()}) — {self.repair}"


class RepairPart(TimeStampedModel):
    repair = models.ForeignKey(
        Repair, verbose_name="Ремонт", on_delete=models.CASCADE, related_name="used_parts"
    )
    part = models.ForeignKey(
        Part, verbose_name="Запчасть", on_delete=models.PROTECT, related_name="repair_parts"
    )
    quantity = models.PositiveIntegerField("Количество", default=1)
    price_at_use = models.DecimalField(
        "Цена на момент использования", max_digits=10, decimal_places=2
    )

    class Meta:
        verbose_name = "Запчасть в ремонте"
        verbose_name_plural = "Запчасти в ремонте"

    def __str__(self):
        return f"{self.part} × {self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_use
