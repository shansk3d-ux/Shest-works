from django.contrib import admin

from .models import Brand, Equipment, EquipmentType


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("typical_equipment_types",)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "model",
        "equipment_type",
        "brand",
        "client",
        "serial_number",
        "is_archived",
    )
    list_filter = ("equipment_type", "brand", "is_archived")
    search_fields = ("model", "serial_number", "client__name", "location")
    autocomplete_fields = ("client", "equipment_type", "brand")
