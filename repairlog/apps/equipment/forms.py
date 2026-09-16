from django import forms

from apps.core.forms import BootstrapModelForm

from .models import Brand, Equipment, EquipmentType


class EquipmentForm(BootstrapModelForm):
    equipment_type = forms.CharField(
        label="Тип оборудования",
        widget=forms.TextInput(attrs={"list": "equipment-type-options", "autocomplete": "off"}),
        help_text="Начните вводить — можно выбрать существующий тип или ввести новый.",
    )
    equipment_type_category = forms.ChoiceField(
        label="Категория нового типа",
        choices=EquipmentType.Category.choices,
        required=False,
        help_text="Нужна только если вводите тип, которого ещё нет в списке.",
    )
    brand = forms.CharField(
        label="Бренд",
        widget=forms.TextInput(attrs={"list": "brand-options", "autocomplete": "off"}),
        help_text="Начните вводить — можно выбрать существующий бренд или ввести новый.",
    )

    class Meta:
        model = Equipment
        fields = [
            "client",
            "equipment_type",
            "equipment_type_category",
            "brand",
            "model",
            "serial_number",
            "year",
            "location",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial["equipment_type"] = self.instance.equipment_type.name
            self.initial["brand"] = self.instance.brand.name

    def clean(self):
        cleaned_data = super().clean()

        type_name = (cleaned_data.get("equipment_type") or "").strip()
        if type_name:
            equipment_type = EquipmentType.objects.filter(name__iexact=type_name).first()
            if not equipment_type:
                category = cleaned_data.get("equipment_type_category")
                if not category:
                    self.add_error(
                        "equipment_type_category",
                        "Укажите категорию для нового типа оборудования.",
                    )
                else:
                    equipment_type = EquipmentType.objects.create(
                        name=type_name, category=category
                    )
            cleaned_data["equipment_type"] = equipment_type

        brand_name = (cleaned_data.get("brand") or "").strip()
        if brand_name:
            brand = Brand.objects.filter(name__iexact=brand_name).first()
            if not brand:
                brand = Brand.objects.create(name=brand_name)
            cleaned_data["brand"] = brand

        return cleaned_data
