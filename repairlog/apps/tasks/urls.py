from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.TaskListView.as_view(), name="list"),
    path("new/", views.TaskCreateView.as_view(), name="create"),
    path("due/", views.TaskDueNotificationsView.as_view(), name="due"),
    path("<int:pk>/", views.TaskDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.TaskUpdateView.as_view(), name="update"),
    path("<int:pk>/complete/", views.TaskCompleteView.as_view(), name="complete"),
    path("<int:pk>/postpone/", views.TaskPostponeView.as_view(), name="postpone"),
    path("<int:pk>/cancel/", views.TaskCancelView.as_view(), name="cancel"),
]
