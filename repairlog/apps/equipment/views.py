from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from apps.core.views import NextUrlRedirectMixin, QuerystringMixin

from .forms import EquipmentForm
from .models import Brand, Equipment, EquipmentType


class EquipmentListView(LoginRequiredMixin, QuerystringMixin, generic.ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"
    context_object_name = "equipment_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = Equipment.objects.select_related("client", "equipment_type", "brand")
        queryset = queryset.filter(is_archived=self._show_archived())

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(model__icontains=query)
                | Q(serial_number__icontains=query)
                | Q(location__icontains=query)
                | Q(client__name__icontains=query)
            )

        equipment_type = self.request.GET.get("equipment_type")
        if equipment_type:
            queryset = queryset.filter(equipment_type_id=equipment_type)

        brand = self.request.GET.get("brand")
        if brand:
            queryset = queryset.filter(brand_id=brand)

        return queryset

    def _show_archived(self):
        return self.request.GET.get("archived") == "1"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["show_archived"] = self._show_archived()
        context["equipment_types"] = EquipmentType.objects.all()
        context["brands"] = Brand.objects.all()
        context["selected_equipment_type"] = self.request.GET.get("equipment_type", "")
        context["selected_brand"] = self.request.GET.get("brand", "")
        return context


class EquipmentDetailView(LoginRequiredMixin, generic.DetailView):
    model = Equipment
    template_name = "equipment/equipment_detail.html"
    context_object_name = "equipment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["repairs"] = self.object.repairs.order_by("-reported_at")
        return context


class EquipmentTypeBrandOptionsMixin:
    """Feeds the create/update form's autocomplete <datalist>s with the current catalog."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["equipment_types"] = EquipmentType.objects.all()
        context["brands"] = Brand.objects.all()
        return context


class EquipmentCreateView(
    LoginRequiredMixin, NextUrlRedirectMixin, EquipmentTypeBrandOptionsMixin, generic.CreateView
):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/equipment_form.html"
    next_url_param_name = "equipment"

    def get_initial(self):
        initial = super().get_initial()
        client_id = self.request.GET.get("client")
        if client_id:
            initial["client"] = client_id
        return initial

    def get_default_success_url(self):
        return reverse_lazy("equipment:detail", args=[self.object.pk])


class EquipmentUpdateView(LoginRequiredMixin, EquipmentTypeBrandOptionsMixin, generic.UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/equipment_form.html"

    def get_success_url(self):
        return reverse_lazy("equipment:detail", args=[self.object.pk])


class EquipmentArchiveView(LoginRequiredMixin, generic.DeleteView):
    """Soft-deletes equipment: a confirmed POST flips is_archived instead of removing the row."""

    model = Equipment
    template_name = "equipment/equipment_confirm_archive.html"
    context_object_name = "equipment"

    def get_success_url(self):
        return reverse_lazy("equipment:detail", args=[self.object.pk])

    def form_valid(self, form):
        self.object.is_archived = True
        self.object.save(update_fields=["is_archived"])
        return HttpResponseRedirect(self.get_success_url())


class EquipmentRestoreView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        equipment = get_object_or_404(Equipment, pk=pk)
        equipment.is_archived = False
        equipment.save(update_fields=["is_archived"])
        return HttpResponseRedirect(reverse_lazy("equipment:detail", args=[equipment.pk]))
