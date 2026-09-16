from django import forms

from apps.core.forms import BootstrapFormMixin, BootstrapModelForm
from apps.repairs.models import Repair

from .models import Task

DATETIME_LOCAL_FORMAT = "%Y-%m-%dT%H:%M"


class TaskForm(BootstrapModelForm):
    due_at = forms.DateTimeField(
        label="Дата и время",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format=DATETIME_LOCAL_FORMAT
        ),
        input_formats=[DATETIME_LOCAL_FORMAT],
    )

    class Meta:
        model = Task
        fields = ["title", "description", "due_at", "repair", "notify_sound"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["repair"].queryset = Repair.objects.select_related(
            "equipment", "equipment__client"
        ).order_by("-reported_at")
        self.fields["repair"].empty_label = "Без привязки к заявке"


class TaskPostponeForm(BootstrapFormMixin, forms.Form):
    postponed_until = forms.DateTimeField(
        label="Отложить до",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format=DATETIME_LOCAL_FORMAT
        ),
        input_formats=[DATETIME_LOCAL_FORMAT],
    )
