"""Страницы клиентов."""

from django.db.models import Sum
from django.shortcuts import render

from .models import Client


def clients(request):
    """Показать список клиентов и сумму предложений каждого клиента."""
    clients_list = Client.objects.annotate(
        total_amount=Sum("proposals__amount", default=0),
    ).order_by("id")
    context = {
        "clients": clients_list,
    }
    return render(request, "clients/client_list.html", context)


def client_detail(request, client_id):
    """Показать клиента. Если его нет — ответ 404."""
    try:
        client = Client.objects.get(pk=client_id)
    except Client.DoesNotExist:
        return render(request, "clients/client_detail.html", status=404)

    client.total_amount = client.proposals.aggregate(
        total=Sum("amount", default=0),
    )["total"]
    context = {
        "client": client,
    }
    return render(request, "clients/client_detail.html", context)
