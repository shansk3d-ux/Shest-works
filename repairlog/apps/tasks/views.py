from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic

from apps.core.views import QuerystringMixin

from .forms import TaskForm, TaskPostponeForm
from .models import Task


class TaskListView(LoginRequiredMixin, QuerystringMixin, generic.ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def get_queryset(self):
        queryset = Task.objects.select_related("repair", "repair__equipment")

        status = self.request.GET.get("status", "active")
        if status == "all":
            pass
        elif status in Task.Status.values:
            queryset = queryset.filter(status=status)
        else:
            queryset = queryset.exclude(status__in=[Task.Status.DONE, Task.Status.CANCELLED])

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))

        return queryset.annotate(
            effective_due=Coalesce("postponed_until", "due_at")
        ).order_by("effective_due")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["selected_status"] = self.request.GET.get("status", "active")
        context["statuses"] = Task.Status.choices
        return context


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}
        if self.object.postponed_until:
            initial["postponed_until"] = self.object.postponed_until
        context["postpone_form"] = TaskPostponeForm(initial=initial)
        return context


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:detail", args=[self.object.pk])


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_success_url(self):
        return reverse_lazy("tasks:detail", args=[self.object.pk])


class TaskCompleteView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.status = Task.Status.DONE
        task.save(update_fields=["status"])
        return redirect("tasks:detail", pk=task.pk)


class TaskCancelView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.status = Task.Status.CANCELLED
        task.save(update_fields=["status"])
        return redirect("tasks:detail", pk=task.pk)


class TaskPostponeView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        form = TaskPostponeForm(request.POST)
        if form.is_valid():
            task.postponed_until = form.cleaned_data["postponed_until"]
            task.status = Task.Status.POSTPONED
            task.notified_at = None
            task.save(update_fields=["postponed_until", "status", "notified_at"])
        else:
            messages.error(request, "Некорректная дата и время отложенной задачи.")
        return redirect("tasks:detail", pk=task.pk)


class TaskDueNotificationsView(LoginRequiredMixin, generic.View):
    """Polled by the browser: returns tasks that just became due and marks them notified."""

    def get(self, request):
        now = timezone.now()
        candidates = Task.objects.filter(
            owner=request.user,
            status__in=[Task.Status.NEW, Task.Status.POSTPONED],
            notified_at__isnull=True,
        )

        due = [task for task in candidates if task.effective_due_at <= now]

        payload = [
            {
                "id": task.pk,
                "title": task.title,
                "description": task.description,
                "url": reverse("tasks:detail", args=[task.pk]),
                "sound_url": static(f"sounds/{task.notify_sound}.wav"),
            }
            for task in due
        ]

        Task.objects.filter(pk__in=[task.pk for task in due]).update(notified_at=now)

        return JsonResponse({"tasks": payload})
