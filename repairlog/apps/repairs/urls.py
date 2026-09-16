from django.urls import path

from . import views

app_name = "repairs"

urlpatterns = [
    path("", views.RepairListView.as_view(), name="list"),
    path("new/", views.RepairWizardClientStepView.as_view(), name="wizard_client"),
    path(
        "new/<int:client_id>/equipment/",
        views.RepairWizardEquipmentStepView.as_view(),
        name="wizard_equipment",
    ),
    path("new/details/", views.RepairCreateView.as_view(), name="create"),
    path("<int:pk>/", views.RepairDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.RepairUpdateView.as_view(), name="update"),
    path("<int:pk>/status/", views.RepairStatusUpdateView.as_view(), name="status"),
    path("<int:pk>/archive/", views.RepairArchiveView.as_view(), name="archive"),
    path("<int:pk>/restore/", views.RepairRestoreView.as_view(), name="restore"),
    path("<int:pk>/photos/", views.RepairPhotoUploadView.as_view(), name="photo_upload"),
    path("photos/<int:pk>/delete/", views.RepairPhotoDeleteView.as_view(), name="photo_delete"),
]
