"""Страницы коммерческих предложений."""

import re
from datetime import date

from django.core.paginator import Paginator
from django.db.models import (
    Avg, CharField, Count, DateField, F, Func, Max, Min, Q, Sum, Value,
)
from django.db.models.functions import Cast, Concat
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from clients.models import Client

from .models import Manager, Proposal

SORT_OPTIONS = {
    "id": ("По порядку добавления", ("id",)),
    "newest": ("Сначала новые", ("-created_date", "id")),
    "oldest": ("Сначала старые", ("created_date", "id")),
    "amount": ("По возрастанию суммы", ("amount", "id")),
    "client": ("По названию клиента", ("client__name", "id")),
}


def expiration_date():
    """Вернуть выражение SQLite для расчёта срока действия через ORM."""
    modifier = Concat(
        Value("+"),
        Cast("validity_days", CharField()),
        Value(" days"),
    )
    return Func(
        F("created_date"), modifier, function="DATE", output_field=DateField(),
    )


def read_date(value):
    """Вернуть дату из GET-параметра, если она задана в формате формы."""
    try:
        selected_date = date.fromisoformat(value)
    except ValueError:
        return None
    if selected_date.isoformat() == value:
        return selected_date
    return None


def proposals(request):
    """Показать предложения с поиском, фильтрами и пагинацией."""
    proposals_list = Proposal.objects.all()
    number = request.GET.get("number", "").strip()
    query = request.GET.get("q", "").strip()
    client_name = request.GET.get("client", "")
    manager_name = request.GET.get("manager", "")
    status = request.GET.get("status", "")
    selected_date = request.GET.get("date", "")
    sort = request.GET.get("sort", "id")
    hide_cancelled = request.GET.get("active") == "1"
    errors = []

    client_names = list(
        Client.objects.order_by("name").values_list("name", flat=True)
        .distinct()
    )
    manager_names = list(
        Manager.objects.order_by("name").values_list("name", flat=True)
        .distinct()
    )
    if number:
        proposals_list = proposals_list.filter(
            number__iregex=re.escape(number),
        )
    if query:
        # Поиск без учёта регистра, в том числе для кириллицы в SQLite.
        pattern = re.escape(query)
        proposals_list = proposals_list.filter(
            Q(number__iregex=pattern)
            | Q(client__name__iregex=pattern)
            | Q(manager__name__iregex=pattern),
        )
    if client_name:
        if client_name in client_names:
            proposals_list = proposals_list.filter(client__name=client_name)
        else:
            errors.append("Выберите клиента из списка.")
    if manager_name:
        if manager_name in manager_names:
            proposals_list = proposals_list.filter(manager__name=manager_name)
        else:
            errors.append("Выберите менеджера из списка.")
    if status:
        if status in Proposal.Status.values:
            proposals_list = proposals_list.filter(status=status)
        else:
            errors.append("Выберите статус из списка.")
    if selected_date:
        active_date = read_date(selected_date)
        if active_date is None:
            errors.append("Введите корректную дату.")
        else:
            proposals_list = proposals_list.alias(
                expires=expiration_date(),
            ).filter(created_date__lte=active_date, expires__gte=active_date)
    if hide_cancelled:
        proposals_list = proposals_list.exclude(
            status=Proposal.Status.CANCELLED,
        )
    if sort not in SORT_OPTIONS:
        sort = "id"
        errors.append("Неизвестная сортировка. Применён обычный порядок.")

    proposals_list = proposals_list.order_by(*SORT_OPTIONS[sort][1])
    cards = proposals_list.annotate(
        client_name=F("client__name"),
        expiration_date=expiration_date(),
    ).values(
        "id", "number", "client_name", "created_date", "expiration_date",
        "status",
    )
    page_obj = Paginator(cards, 2).get_page(request.GET.get("page"))
    context = {
        "proposals": page_obj.object_list,
        "page_obj": page_obj,
        "client_names": client_names,
        "manager_names": manager_names,
        "statuses": Proposal.Status.choices,
        "sort_options": SORT_OPTIONS,
        "number": number,
        "query": query,
        "client_name": client_name,
        "manager_name": manager_name,
        "status": status,
        "selected_date": selected_date,
        "sort": sort,
        "hide_cancelled": hide_cancelled,
        "errors": errors,
    }
    return render(request, "proposals/proposal_list.html", context)


def proposal_search(request):
    """Найти предложения, срок действия которых включает выбранную дату."""
    selected_date = request.GET.get("date", "")
    search_date = read_date(selected_date)
    proposals_list = []
    if search_date is not None:
        proposals_list = Proposal.objects.annotate(
            client_name=F("client__name"),
            expiration_date=expiration_date(),
        ).filter(
            created_date__lte=search_date,
            expiration_date__gte=search_date,
        ).order_by("id").values(
            "id", "number", "client_name", "created_date", "expiration_date",
            "status",
        )
    context = {
        "proposals": proposals_list,
        "selected_date": selected_date,
        "invalid_date": bool(selected_date and search_date is None),
    }
    return render(request, "proposals/proposal_search.html", context)


def proposal_statistics(request):
    """Показать статистику по клиентам и суммы действующих предложений."""
    clients_list = Client.objects.annotate(
        proposals_count=Count("proposals"),
    ).order_by("id")
    active_proposals = Proposal.objects.exclude(
        status=Proposal.Status.CANCELLED,
    )
    summary = active_proposals.aggregate(
        count=Count("id"),
        total=Sum("amount", default=0),
        average=Avg("amount"),
        minimum=Min("amount"),
        maximum=Max("amount"),
    )
    context = {
        "clients": clients_list,
        "summary": summary,
    }
    return render(request, "proposals/proposal_statistics.html", context)


def proposal_detail(request, proposal_id):
    """Показать одно предложение. Если его нет — ответ 404."""
    queryset = Proposal.objects.select_related("client", "manager")
    try:
        proposal = get_object_or_404(queryset, pk=proposal_id)
    except Http404:
        return render(request, "proposals/proposal_detail.html", status=404)
    context = {
        "proposal": proposal,
    }
    return render(request, "proposals/proposal_detail.html", context)
