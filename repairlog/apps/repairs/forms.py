from django import forms

from apps.core.forms import BootstrapFormMixin, BootstrapModelForm
from apps.knowledge.models import Fault

from .models import Repair

DATE_WIDGET = forms.DateInput(attrs={"type": "date"})


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
