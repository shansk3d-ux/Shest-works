from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.GlobalSearchView.as_view(), name="search"),
    path("service-worker.js", views.ServiceWorkerView.as_view(), name="service_worker"),
]
