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

# What each brand actually makes, so equipment-form suggestions are useful from
# the first use — not just after enough equipment has been logged by hand.
# Household appliance makers (Electrolux, Bosch, Samsung, LG, Zanussi,
# Whirlpool, Indesit, Gorenje) all sell essentially the same lineup, so
# they share one list; the rest are commercial/HoReCa specialists with a
# narrower real-world range.
_HOUSEHOLD_LINEUP = [
    "Стиральная машина",
    "Холодильник",
    "Посудомоечная машина (бытовая)",
    "Микроволновая печь",
    "Духовой шкаф",
    "Сушильная машина",
]

BRAND_TYPICAL_EQUIPMENT = {
    # Combi-steamer specialists.
    "Rational": ["Пароконвектомат"],
    "Unox": ["Пароконвектомат"],
    "Convotherm": ["Пароконвектомат"],
    # Warewashing specialists.
    "Winterhalter": ["Посудомоечная машина (кухонная)"],
    "Hobart": ["Посудомоечная машина (кухонная)", "Тестомес"],
    # Household appliance makers.
    "Electrolux": _HOUSEHOLD_LINEUP,
    "Bosch": _HOUSEHOLD_LINEUP,
    "Samsung": ["Стиральная машина", "Холодильник", "Микроволновая печь", "Сушильная машина"],
    "LG": ["Стиральная машина", "Холодильник", "Микроволновая печь", "Сушильная машина"],
    "Zanussi": [
        "Стиральная машина",
        "Холодильник",
        "Посудомоечная машина (бытовая)",
        "Духовой шкаф",
    ],
    "Whirlpool": _HOUSEHOLD_LINEUP,
    "Indesit": [
        "Стиральная машина",
        "Холодильник",
        "Посудомоечная машина (бытовая)",
        "Духовой шкаф",
    ],
    "Gorenje": [
        "Стиральная машина",
        "Холодильник",
        "Посудомоечная машина (бытовая)",
        "Духовой шкаф",
        "Микроволновая печь",
    ],
    # Abat (Чувашторгтехника): broad Russian HoReCa equipment maker —
    # combi ovens, ranges, dough mixers, commercial fridges and dishwashers.
    "Abat": [
        "Пароконвектомат",
        "Плита индукционная",
        "Холодильный шкаф",
        "Посудомоечная машина (кухонная)",
        "Тестомес",
        "Промышленный холодильник",
    ],
    # Polair: Russian commercial refrigeration specialist.
    "Polair": [
        "Холодильный шкаф",
        "Морозильный ларь",
        "Витрина холодильная",
        "Промышленный холодильник",
        "Компрессор холодильный",
    ],
}


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
            brand, created = Brand.objects.get_or_create(name=name)
            created_brands += int(created)

            typical_names = BRAND_TYPICAL_EQUIPMENT.get(name, [])
            if typical_names:
                brand.typical_equipment_types.set(
                    EquipmentType.objects.filter(name__in=typical_names)
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: добавлено {created_types} новых типов оборудования, "
                f"{created_brands} новых брендов."
            )
        )
