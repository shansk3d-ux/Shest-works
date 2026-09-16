import django_filters
from django import forms
from django.db.models import Q

from .models import Repair


class RepairFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_search", label="Поиск")
    reported_from = django_filters.DateFilter(
        field_name="reported_at",
        lookup_expr="gte",
        label="С даты",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    reported_to = django_filters.DateFilter(
        field_name="reported_at",
        lookup_expr="lte",
        label="По дату",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Repair
        fields = ["status", "master"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(error_code__icontains=value)
            | Q(symptom__icontains=value)
            | Q(equipment__model__icontains=value)
            | Q(equipment__serial_number__icontains=value)
            | Q(equipment__client__name__icontains=value)
        )
