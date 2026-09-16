from django.core.management.base import BaseCommand
from django.db import transaction

from apps.equipment.models import Brand, EquipmentType

EQUIPMENT_TYPES = [
    ("Стиральная машина", EquipmentType.Category.HOUSEHOLD),
    ("Сушильная машина", EquipmentType.Category.HOUSEHOLD),
    ("Холодильник", EquipmentType.Category.HOUSEHOLD),
    ("Посудомоечная машина (бытовая)", EquipmentType.Category.HOUSEHOLD),
    ("Микроволновая печь", EquipmentType.Category.HOUSEHOLD),
    ("Духовой шкаф", EquipmentType.Category.HOUSEHOLD),
    ("Пароконвектомат", EquipmentType.Category.KITCHEN),
    ("Посудомоечная машина (кухонная)", EquipmentType.Category.KITCHEN),
    ("Тестомес", EquipmentType.Category.KITCHEN),
    ("Блендер", EquipmentType.Category.KITCHEN),
    ("Кофемашина", EquipmentType.Category.KITCHEN),
    ("Плита индукционная", EquipmentType.Category.KITCHEN),
    ("Холодильный шкаф", EquipmentType.Category.RESTAURANT),
    ("Морозильный ларь", EquipmentType.Category.RESTAURANT),
    ("Барная стойка", EquipmentType.Category.RESTAURANT),
    ("Льдогенератор", EquipmentType.Category.RESTAURANT),
    ("Витрина холодильная", EquipmentType.Category.RESTAURANT),
    ("Промышленная стиральная машина", EquipmentType.Category.INDUSTRIAL),
    ("Промышленный холодильник", EquipmentType.Category.INDUSTRIAL),
    ("Компрессор холодильный", EquipmentType.Category.INDUSTRIAL),
    ("Вентиляционная установка", EquipmentType.Category.INDUSTRIAL),
]

BRANDS = [
    "Rational",
    "Unox",
    "Electrolux",
    "Winterhalter",
    "Hobart",
    "Bosch",
    "Samsung",
    "LG",
    "Zanussi",
    "Whirlpool",
    "Indesit",
    "Gorenje",
    "Convotherm",
    "Abat",
    "Polair",
]


class Command(BaseCommand):
    help = "Заполняет справочники типов оборудования и брендов начальными данными"

    @transaction.atomic
    def handle(self, *args, **options):
        created_types = 0
        for name, category in EQUIPMENT_TYPES:
            _, created = EquipmentType.objects.get_or_create(
                name=name, defaults={"category": category}
            )
            created_types += int(created)

        created_brands = 0
        for name in BRANDS:
            _, created = Brand.objects.get_or_create(name=name)
            created_brands += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: добавлено {created_types} новых типов оборудования, "
                f"{created_brands} новых брендов."
            )
        )
