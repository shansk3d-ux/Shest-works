from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.core.forms import LoginForm

admin.site.site_header = "RepairLog"
admin.site.site_title = "RepairLog"
admin.site.index_title = "Администрирование"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(authentication_form=LoginForm),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("clients/", include("apps.clients.urls")),
    path("equipment/", include("apps.equipment.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
