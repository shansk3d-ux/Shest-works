from django.urls import path

from . import views

app_name = "equipment"

urlpatterns = [
    path("", views.EquipmentListView.as_view(), name="list"),
    path("new/", views.EquipmentCreateView.as_view(), name="create"),
    path(
        "type-suggestions/",
        views.EquipmentTypeSuggestionsView.as_view(),
        name="type_suggestions",
    ),
    path("<int:pk>/", views.EquipmentDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.EquipmentUpdateView.as_view(), name="update"),
    path("<int:pk>/archive/", views.EquipmentArchiveView.as_view(), name="archive"),
    path("<int:pk>/restore/", views.EquipmentRestoreView.as_view(), name="restore"),
]
