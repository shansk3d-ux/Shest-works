from django import forms

from apps.core.forms import BootstrapModelForm

from .models import Part


class PartForm(BootstrapModelForm):
    class Meta:
        model = Part
        fields = ["name", "kind", "article", "brand", "price", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
