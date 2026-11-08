"""Клиенты в панели администратора."""

from django.contrib import admin

from proposals.admin import ProposalInline

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    ordering = ("name", "id")
    list_per_page = 20
    readonly_fields = ("slug",)
    inlines = (ProposalInline,)
