from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic

from apps.clients.models import Client
from apps.core.forms import apply_bootstrap_classes
from apps.core.views import QuerystringMixin
from apps.equipment.models import Equipment

from .filters import RepairFilter
from .forms import RepairCreateForm, RepairStatusForm, RepairUpdateForm
from .models import Repair


class RepairListView(LoginRequiredMixin, QuerystringMixin, generic.ListView):
    model = Repair
    template_name = "repairs/repair_list.html"
    context_object_name = "repairs"
    paginate_by = 20

    def get_queryset(self):
        show_archived = self.request.GET.get("archived") == "1"
        queryset = Repair.objects.select_related(
            "equipment", "equipment__client", "master"
        ).filter(is_archived=show_archived)
        self.filterset = RepairFilter(self.request.GET, queryset=queryset)
        apply_bootstrap_classes(self.filterset.form)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        context["show_archived"] = self.request.GET.get("archived") == "1"
        return context


class RepairDetailView(LoginRequiredMixin, generic.DetailView):
    model = Repair
    template_name = "repairs/repair_detail.html"
    context_object_name = "repair"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_form"] = RepairStatusForm(initial={"status": self.object.status})
        return context


class RepairWizardClientStepView(LoginRequiredMixin, generic.ListView):
    """Repair creation, step 1: pick (or search for) the client."""

    model = Client
    template_name = "repairs/wizard_client.html"
    context_object_name = "clients"
    paginate_by = 20

    def get_queryset(self):
        queryset = Client.objects.all()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class RepairWizardEquipmentStepView(LoginRequiredMixin, generic.DetailView):
    """Repair creation, step 2: pick existing equipment or add new on the fly."""

    model = Client
    template_name = "repairs/wizard_equipment.html"
    context_object_name = "client"
    pk_url_kwarg = "client_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["equipment_list"] = self.object.equipment.filter(is_archived=False)
        next_url = f"{reverse('repairs:create')}?{urlencode({'client': self.object.pk})}"
        context["add_equipment_url"] = (
            f"{reverse('equipment:create')}?"
            f"{urlencode({'client': self.object.pk, 'next': next_url})}"
        )
        return context


class RepairCreateView(LoginRequiredMixin, generic.CreateView):
    """Repair creation, step 3: describe the symptom and create the repair."""

    model = Repair
    form_class = RepairCreateForm
    template_name = "repairs/repair_wizard_details.html"

    def dispatch(self, request, *args, **kwargs):
        equipment_id = request.GET.get("equipment") or request.POST.get("equipment")
        self.equipment = get_object_or_404(Equipment, pk=equipment_id)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial["master"] = self.request.user.pk
        initial["reported_at"] = timezone.localdate()
        return initial

    def form_valid(self, form):
        form.instance.equipment = self.equipment
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["equipment"] = self.equipment
        return context

    def get_success_url(self):
        return reverse_lazy("repairs:detail", args=[self.object.pk])


class RepairUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Repair
    form_class = RepairUpdateForm
    template_name = "repairs/repair_form.html"

    def get_success_url(self):
        return reverse_lazy("repairs:detail", args=[self.object.pk])


class RepairStatusUpdateView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        repair = get_object_or_404(Repair, pk=pk)
        form = RepairStatusForm(request.POST)
        if form.is_valid():
            repair.status = form.cleaned_data["status"]
            if repair.status == Repair.Status.DONE and not repair.completed_at:
                repair.completed_at = timezone.localdate()
            repair.save(update_fields=["status", "completed_at"])
        else:
            messages.error(request, "Некорректный статус.")
        return redirect("repairs:detail", pk=repair.pk)


class RepairArchiveView(LoginRequiredMixin, generic.DeleteView):
    """Soft-deletes a repair: a confirmed POST flips is_archived instead of removing the row."""

    model = Repair
    template_name = "repairs/repair_confirm_archive.html"
    context_object_name = "repair"

    def get_success_url(self):
        return reverse_lazy("repairs:detail", args=[self.object.pk])

    def form_valid(self, form):
        self.object.is_archived = True
        self.object.save(update_fields=["is_archived"])
        return HttpResponseRedirect(self.get_success_url())


class RepairRestoreView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        repair = get_object_or_404(Repair, pk=pk)
        repair.is_archived = False
        repair.save(update_fields=["is_archived"])
        return HttpResponseRedirect(reverse_lazy("repairs:detail", args=[repair.pk]))
