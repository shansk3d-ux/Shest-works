import json

from django import forms
from django.urls import reverse

from apps.core.forms import BootstrapFormMixin, BootstrapModelForm
from apps.knowledge.models import Fault
from apps.parts.models import Part

from .models import Repair, RepairPhoto

DATE_WIDGET = forms.DateInput(attrs={"type": "date"})


def _attach_fault_suggestions(field, equipment_type_id):
    """Wires up the error_code field to live-load matching Fault entries via HTMX."""
    if not equipment_type_id:
        return
    field.widget.attrs.update(
        {
            "hx-get": reverse("knowledge:fault_suggestions"),
            "hx-trigger": "keyup changed delay:400ms, load",
            "hx-target": "#fault-suggestions",
            "hx-swap": "innerHTML",
            "hx-vals": json.dumps({"equipment_type": equipment_type_id}),
        }
    )


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        # No "capture" attribute: that forces mobile browsers straight into the
        # camera, skipping the OS picker that also offers gallery/files.
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data]
        return single_file_clean(data, initial)


class RepairCreateForm(BootstrapModelForm):
    class Meta:
        model = Repair
        fields = ["master", "reported_at", "symptom", "error_code"]
        widgets = {
            "reported_at": DATE_WIDGET,
            "symptom": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, equipment_type_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        _attach_fault_suggestions(self.fields["error_code"], equipment_type_id)


class RepairUpdateForm(BootstrapModelForm):
    class Meta:
        model = Repair
        fields = [
            "master",
            "status",
            "reported_at",
            "completed_at",
            "symptom",
            "error_code",
            "diagnosis",
            "work_done",
            "fault",
            "labor_cost",
            "parts_cost",
            "warranty_until",
        ]
        widgets = {
            "reported_at": DATE_WIDGET,
            "completed_at": DATE_WIDGET,
            "warranty_until": DATE_WIDGET,
            "symptom": forms.Textarea(attrs={"rows": 3}),
            "diagnosis": forms.Textarea(attrs={"rows": 3}),
            "work_done": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, equipment_type_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fault"].queryset = Fault.objects.select_related(
            "equipment_type", "brand"
        ).order_by("equipment_type__name", "error_code")
        self.fields["fault"].empty_label = "Не выбрано"
        _attach_fault_suggestions(self.fields["error_code"], equipment_type_id)


class RepairStatusForm(BootstrapFormMixin, forms.Form):
    status = forms.ChoiceField(label="Статус", choices=Repair.Status.choices)


class RepairPhotoUploadForm(BootstrapFormMixin, forms.Form):
    images = MultipleFileField(label="Фото")
    stage = forms.ChoiceField(
        label="Этап", choices=RepairPhoto.Stage.choices, initial=RepairPhoto.Stage.BEFORE
    )
    caption = forms.CharField(label="Подпись (опционально)", required=False)


class RepairPartAddForm(BootstrapFormMixin, forms.Form):
    part = forms.ChoiceField(label="Запчасть/услуга")
    part_new_name = forms.CharField(label="Название новой позиции", required=False)
    part_new_kind = forms.ChoiceField(
        label="Тип", choices=Part.Kind.choices, required=False, initial=Part.Kind.PART
    )
    part_new_price = forms.DecimalField(
        label="Цена", max_digits=10, decimal_places=2, required=False, min_value=0
    )
    quantity = forms.IntegerField(label="Количество", min_value=1, initial=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(part.name, part.name) for part in Part.objects.order_by("name")]
        choices.append(("__new__", "+ Новая запчасть/услуга…"))
        self.fields["part"].choices = choices

    def clean(self):
        cleaned_data = super().clean()

        part_value = cleaned_data.get("part")
        resolved_part = None
        if part_value == "__new__":
            new_name = (cleaned_data.get("part_new_name") or "").strip()
            price = cleaned_data.get("part_new_price")
            if not new_name:
                self.add_error("part_new_name", "Введите название.")
            elif price is None:
                self.add_error("part_new_price", "Укажите цену.")
            else:
                kind = cleaned_data.get("part_new_kind") or Part.Kind.PART
                resolved_part = Part.objects.filter(name__iexact=new_name).first()
                if not resolved_part:
                    resolved_part = Part.objects.create(name=new_name, kind=kind, price=price)
        elif part_value:
            resolved_part = Part.objects.filter(name=part_value).first()
        cleaned_data["part"] = resolved_part

        new_part_errors = self.errors.get("part_new_name") or self.errors.get("part_new_price")
        if resolved_part is None and not new_part_errors:
            self.add_error("part", "Выберите запчасть/услугу.")

        return cleaned_data
