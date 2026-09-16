from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views import generic

from .models import Fault


class FaultSuggestionsView(LoginRequiredMixin, generic.ListView):
    """HTMX fragment: past Fault entries matching the equipment type / error code
    being typed into a repair form, most-encountered first."""

    template_name = "knowledge/_fault_suggestions.html"
    context_object_name = "faults"

    def get_queryset(self):
        equipment_type_id = self.request.GET.get("equipment_type", "").strip()
        if not equipment_type_id:
            return Fault.objects.none()

        queryset = Fault.objects.filter(equipment_type_id=equipment_type_id).select_related(
            "equipment_type", "brand"
        )

        error_code = self.request.GET.get("error_code", "").strip()
        if error_code:
            queryset = queryset.filter(error_code__icontains=error_code)

        return queryset.annotate(repairs_count=Count("repairs")).order_by(
            "-repairs_count", "error_code"
        )[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["searched"] = bool(self.request.GET.get("equipment_type"))
        return context
