from django import forms

from apps.core.forms import BootstrapModelForm

from .models import Equipment


class EquipmentForm(BootstrapModelForm):
    class Meta:
        model = Equipment
        fields = [
            "client",
            "equipment_type",
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
