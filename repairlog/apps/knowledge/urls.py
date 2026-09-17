from django.urls import path

from . import views

app_name = "knowledge"

urlpatterns = [
    path("fault-suggestions/", views.FaultSuggestionsView.as_view(), name="fault_suggestions"),
]
