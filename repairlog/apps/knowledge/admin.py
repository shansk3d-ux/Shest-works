from django.contrib import admin

from .models import Fault


@admin.register(Fault)
class FaultAdmin(admin.ModelAdmin):
    list_display = ("equipment_type", "brand", "error_code", "model_pattern")
    list_filter = ("equipment_type", "brand")
    search_fields = ("error_code", "symptom", "cause", "solution", "model_pattern")
    autocomplete_fields = ("equipment_type", "brand")
