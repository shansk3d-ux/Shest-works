from django import forms

from apps.core.forms import BootstrapFormMixin, BootstrapModelForm
from apps.knowledge.models import Fault

from .models import Repair, RepairPhoto

DATE_WIDGET = forms.DateInput(attrs={"type": "date"})


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "widget", MultipleFileInput(attrs={"accept": "image/*", "capture": "environment"})
        )
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fault"].queryset = Fault.objects.select_related(
            "equipment_type", "brand"
        ).order_by("equipment_type__name", "error_code")
        self.fields["fault"].empty_label = "Не выбрано"


class RepairStatusForm(BootstrapFormMixin, forms.Form):
    status = forms.ChoiceField(label="Статус", choices=Repair.Status.choices)


class RepairPhotoUploadForm(BootstrapFormMixin, forms.Form):
    images = MultipleFileField(label="Фото")
    stage = forms.ChoiceField(
        label="Этап", choices=RepairPhoto.Stage.choices, initial=RepairPhoto.Stage.BEFORE
    )
    caption = forms.CharField(label="Подпись (опционально)", required=False)
