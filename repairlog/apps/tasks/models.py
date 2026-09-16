from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.repairs.models import Repair


class Task(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Завершена"
        POSTPONED = "postponed", "Отложена"
        CANCELLED = "cancelled", "Отменена"

    class NotifySound(models.TextChoices):
        DEFAULT = "default", "Стандартный"
        BELL = "bell", "Колокольчик"
        CHIME = "chime", "Перезвон"
        ALERT = "alert", "Тревога"

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    due_at = models.DateTimeField("Дата и время")
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW
    )
    postponed_until = models.DateTimeField("Отложить до", null=True, blank=True)
    repair = models.ForeignKey(
        Repair,
        verbose_name="Заявка",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Ответственный",
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    notify_sound = models.CharField(
        "Звук уведомления",
        max_length=20,
        choices=NotifySound.choices,
        default=NotifySound.DEFAULT,
    )
    notified_at = models.DateTimeField("Уведомление отправлено", null=True, blank=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["due_at"]

    def __str__(self):
        return self.title

    @property
    def effective_due_at(self):
        return self.postponed_until or self.due_at

    @property
    def is_overdue(self):
        return self.status in (self.Status.NEW, self.Status.POSTPONED) and (
            self.effective_due_at <= timezone.now()
        )
