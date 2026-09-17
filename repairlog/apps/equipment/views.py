from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from apps.core.views import NextUrlRedirectMixin, QuerystringMixin

from .forms import NEW_OPTION_VALUE, EquipmentForm
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


class EquipmentTypeSuggestionsView(LoginRequiredMixin, generic.TemplateView):
    """HTMX fragment: re-renders the equipment_type <select>'s options, grouping the
    types characteristic of the chosen brand ahead of the rest — triggered whenever
    the brand field changes on the equipment form. "Characteristic" combines the
    brand's real-world product lineup (Brand.typical_equipment_types, from the
    seed command) with whatever types this brand has actually been logged with
    here, so suggestions are useful from the first use, not just after enough
    equipment has piled up."""

    template_name = "equipment/_equipment_type_options.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand_name = self.request.GET.get("brand", "").strip()
        selected_type = self.request.GET.get("equipment_type", "").strip()

        characteristic_ids = set()
        if brand_name and brand_name != NEW_OPTION_VALUE:
            brand = Brand.objects.filter(name=brand_name).first()
            if brand:
                characteristic_ids.update(
                    brand.typical_equipment_types.values_list("id", flat=True)
                )
            characteristic_ids.update(
                EquipmentType.objects.filter(equipment__brand__name=brand_name)
                .distinct()
                .values_list("id", flat=True)
            )

        characteristic_types = EquipmentType.objects.filter(
            id__in=characteristic_ids
        ).order_by("name")
        characteristic_names = [t.name for t in characteristic_types]

        # The previous selection may no longer be relevant to the newly picked
        # brand (e.g. switching from one brand to another) — jump to the top
        # suggestion instead of leaving an unrelated type selected. A value
        # that's already in the suggested set (as it always is when this fires
        # on loading the edit form for existing equipment) is left untouched.
        if (
            characteristic_names
            and selected_type != NEW_OPTION_VALUE
            and selected_type not in characteristic_names
        ):
            selected_type = characteristic_names[0]

        context["brand_name"] = brand_name
        context["characteristic_types"] = characteristic_types
        context["other_types"] = EquipmentType.objects.exclude(
            id__in=characteristic_ids
        ).order_by("name")
        context["selected_type"] = selected_type
        return context


class EquipmentDetailView(LoginRequiredMixin, generic.DetailView):
    model = Equipment
    template_name = "equipment/equipment_detail.html"
    context_object_name = "equipment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["repairs"] = self.object.repairs.order_by("-reported_at")
        return context


class EquipmentCreateView(LoginRequiredMixin, NextUrlRedirectMixin, generic.CreateView):
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


class EquipmentUpdateView(LoginRequiredMixin, generic.UpdateView):
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
