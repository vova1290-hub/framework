"""Предложения и менеджеры в панели администратора."""

from django.contrib import admin

from .models import Manager, Proposal

admin.site.register(Manager)


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("number", "client", "manager", "created_date", "status")
    list_filter = ("status",)
    list_select_related = ("client", "manager")
    search_fields = ("number", "client__name", "manager__name")
