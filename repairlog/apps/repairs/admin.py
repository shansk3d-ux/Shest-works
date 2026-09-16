from django.contrib import admin

from .models import Repair, RepairPart, RepairPhoto


class RepairPhotoInline(admin.TabularInline):
    model = RepairPhoto
    extra = 0


class RepairPartInline(admin.TabularInline):
    model = RepairPart
    extra = 0
    autocomplete_fields = ("part",)


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "equipment",
        "master",
        "status",
        "reported_at",
        "completed_at",
        "total_cost",
        "is_archived",
    )
    list_filter = ("status", "master", "is_archived")
    search_fields = (
        "error_code",
        "symptom",
        "diagnosis",
        "work_done",
        "equipment__serial_number",
        "equipment__model",
    )
    autocomplete_fields = ("equipment", "master", "fault")
    date_hierarchy = "reported_at"
    inlines = [RepairPartInline, RepairPhotoInline]

    @admin.display(description="Итого")
    def total_cost(self, obj):
        return obj.total_cost
