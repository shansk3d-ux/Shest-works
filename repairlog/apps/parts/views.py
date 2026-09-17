from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError, Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from apps.core.views import QuerystringMixin

from .forms import PartForm
from .models import Part


class PartListView(LoginRequiredMixin, QuerystringMixin, generic.ListView):
    model = Part
    template_name = "parts/part_list.html"
    context_object_name = "parts"
    paginate_by = 20

    def get_queryset(self):
        queryset = Part.objects.select_related("brand")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(article__icontains=query))

        kind = self.request.GET.get("kind")
        if kind in Part.Kind.values:
            queryset = queryset.filter(kind=kind)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["selected_kind"] = self.request.GET.get("kind", "")
        context["kinds"] = Part.Kind.choices
        return context


class PartDetailView(LoginRequiredMixin, generic.DetailView):
    model = Part
    template_name = "parts/part_detail.html"
    context_object_name = "part"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["used_in"] = self.object.repair_parts.select_related(
            "repair", "repair__equipment"
        ).order_by("-repair__reported_at")
        return context


class PartCreateView(LoginRequiredMixin, generic.CreateView):
    model = Part
    form_class = PartForm
    template_name = "parts/part_form.html"

    def get_success_url(self):
        return reverse_lazy("parts:detail", args=[self.object.pk])


class PartUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Part
    form_class = PartForm
    template_name = "parts/part_form.html"

    def get_success_url(self):
        return reverse_lazy("parts:detail", args=[self.object.pk])


class PartDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Part
    template_name = "parts/part_confirm_delete.html"
    success_url = reverse_lazy("parts:list")
    context_object_name = "part"

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Нельзя удалить запчасть: она использована в одном или нескольких ремонтах.",
            )
            return HttpResponseRedirect(reverse_lazy("parts:detail", args=[self.object.pk]))
