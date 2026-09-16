from django import forms
from django.contrib.auth.forms import AuthenticationForm


def apply_bootstrap_classes(form):
    """Adds Bootstrap classes to every field widget on `form`, sized for touch input."""
    for field in form.fields.values():
        existing = field.widget.attrs.get("class", "")
        if isinstance(field.widget, forms.CheckboxInput):
            css_class = "form-check-input"
        elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
            css_class = "form-select form-select-lg"
        else:
            css_class = "form-control form-control-lg"
        field.widget.attrs["class"] = f"{existing} {css_class}".strip()


class BootstrapFormMixin:
    """Adds Bootstrap classes to every field widget, sized for touch input."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_classes(self)


class BootstrapModelForm(BootstrapFormMixin, forms.ModelForm):
    pass


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(
            attrs={"class": "form-control form-control-lg", "autofocus": True}
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}),
    )
