from django.contrib import admin

from .models import Part


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("name", "article", "brand", "price")
    list_filter = ("brand",)
    search_fields = ("name", "article")
    autocomplete_fields = ("brand",)
