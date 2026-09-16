from django import forms

from apps.core.forms import BootstrapModelForm

from .models import Client


class ClientForm(BootstrapModelForm):
    class Meta:
        model = Client
        fields = ["name", "client_type", "phone", "email", "address", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
