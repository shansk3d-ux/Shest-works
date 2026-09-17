from django.contrib import admin

from .models import Part


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "article", "brand", "price")
    list_filter = ("kind", "brand")
    search_fields = ("name", "article")
    autocomplete_fields = ("brand",)
