from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "due_at", "postponed_until", "owner", "repair")
    list_filter = ("status", "owner")
    search_fields = ("title", "description")
    autocomplete_fields = ("repair", "owner")
    date_hierarchy = "due_at"
