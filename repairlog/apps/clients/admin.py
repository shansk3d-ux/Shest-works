from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "client_type", "phone", "email", "created_at")
    list_filter = ("client_type",)
    search_fields = ("name", "phone", "email", "address")
