from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import TimeStampedModel


class Client(TimeStampedModel):
    class ClientType(models.TextChoices):
        INDIVIDUAL = "individual", "Частное лицо"
        ORGANIZATION = "organization", "Организация"

    name = models.CharField("Название / ФИО", max_length=255)
    client_type = models.CharField(
        "Тип клиента",
        max_length=20,
        choices=ClientType.choices,
        default=ClientType.INDIVIDUAL,
    )
    inn = models.CharField(
        "ИНН",
        max_length=12,
        blank=True,
        validators=[
            RegexValidator(
                r"^(\d{10}|\d{12})$",
                "ИНН — это 10 цифр у организации или 12 цифр у физлица и ИП.",
            )
        ],
    )
    phone = models.CharField("Телефон", max_length=32, blank=True)
    email = models.EmailField("E-mail", blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    notes = models.TextField("Заметки", blank=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["name"]

    def __str__(self):
        return self.name
