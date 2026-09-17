from django import forms

from apps.core.forms import BootstrapModelForm

from .models import Brand, Equipment, EquipmentType

NEW_OPTION_VALUE = "__new__"
NEW_TYPE_LABEL = "+ Новый тип оборудования…"
NEW_BRAND_LABEL = "+ Новый бренд…"


class EquipmentForm(BootstrapModelForm):
    equipment_type = forms.ChoiceField(label="Тип оборудования")
    equipment_type_new_name = forms.CharField(
        label="Название нового типа", required=False
    )
    equipment_type_category = forms.ChoiceField(
        label="Категория нового типа",
        choices=EquipmentType.Category.choices,
        required=False,
    )
    brand = forms.ChoiceField(label="Бренд")
    brand_new_name = forms.CharField(label="Название нового бренда", required=False)

    class Meta:
        model = Equipment
        fields = [
            "client",
            "equipment_type",
            "equipment_type_new_name",
            "equipment_type_category",
            "brand",
            "brand_new_name",
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

        type_choices = [(t.name, t.name) for t in EquipmentType.objects.order_by("name")]
        type_choices.append((NEW_OPTION_VALUE, NEW_TYPE_LABEL))
        self.fields["equipment_type"].choices = type_choices

        brand_choices = [(b.name, b.name) for b in Brand.objects.order_by("name")]
        brand_choices.append((NEW_OPTION_VALUE, NEW_BRAND_LABEL))
        self.fields["brand"].choices = brand_choices

        if self.instance.pk:
            self.initial["equipment_type"] = self.instance.equipment_type.name
            self.initial["brand"] = self.instance.brand.name

    def clean(self):
        cleaned_data = super().clean()

        type_value = cleaned_data.get("equipment_type")
        resolved_type = None
        if type_value == NEW_OPTION_VALUE:
            new_name = (cleaned_data.get("equipment_type_new_name") or "").strip()
            category = cleaned_data.get("equipment_type_category")
            if not new_name:
                self.add_error("equipment_type_new_name", "Введите название нового типа.")
            elif not category:
                self.add_error(
                    "equipment_type_category",
                    "Укажите категорию для нового типа оборудования.",
                )
            else:
                resolved_type = EquipmentType.objects.filter(name__iexact=new_name).first()
                if not resolved_type:
                    resolved_type = EquipmentType.objects.create(
                        name=new_name, category=category
                    )
        elif type_value:
            resolved_type = EquipmentType.objects.filter(name=type_value).first()
        # Always overwrite: a raw "__new__" (or any other string) left in
        # cleaned_data would otherwise crash ModelForm._post_clean() when it
        # tries to assign it straight to the equipment_type FK.
        cleaned_data["equipment_type"] = resolved_type
        type_subfield_errors = self.errors.get("equipment_type_new_name") or self.errors.get(
            "equipment_type_category"
        )
        if resolved_type is None and not type_subfield_errors:
            self.add_error("equipment_type", "Выберите тип оборудования.")

        brand_value = cleaned_data.get("brand")
        resolved_brand = None
        if brand_value == NEW_OPTION_VALUE:
            new_brand_name = (cleaned_data.get("brand_new_name") or "").strip()
            if not new_brand_name:
                self.add_error("brand_new_name", "Введите название нового бренда.")
            else:
                resolved_brand = Brand.objects.filter(name__iexact=new_brand_name).first()
                if not resolved_brand:
                    resolved_brand = Brand.objects.create(name=new_brand_name)
        elif brand_value:
            resolved_brand = Brand.objects.filter(name=brand_value).first()
        cleaned_data["brand"] = resolved_brand
        if resolved_brand is None and not self.errors.get("brand_new_name"):
            self.add_error("brand", "Выберите бренд.")

        return cleaned_data
