"""Предложения и менеджеры в панели администратора."""

from django.contrib import admin

from .models import Manager, Proposal

admin.site.site_header = "Управление коммерческими предложениями"
admin.site.site_title = "Учёт КП"
admin.site.index_title = "Данные проекта"


class ProposalInline(admin.TabularInline):
    model = Proposal
    fields = ("number", "status", "created_date", "amount")
    readonly_fields = fields
    show_change_link = True
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name", "id")
    list_per_page = 20
    inlines = (ProposalInline,)


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        "number", "client", "manager", "created_date", "status",
        "final_amount",
    )
    list_filter = ("status", "client", "manager", "created_date")
    list_select_related = ("client", "manager")
    search_fields = ("number", "client__name", "manager__name")
    ordering = ("-created_date", "id")
    list_per_page = 20
    date_hierarchy = "created_date"
    autocomplete_fields = ("client", "manager")
    readonly_fields = ("stored_amount",)

    @admin.display(description="Итоговая сумма")
    def stored_amount(self, obj):
        if obj and obj.pk:
            return obj.final_amount
        return None
