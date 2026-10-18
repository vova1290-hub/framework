"""Страницы клиентов."""

from django.shortcuts import render

from models.clients import find_client_by_id
from storage import load_clients, load_managers, load_proposals


def _proposal_list():
    """Загрузить предложения вместе с клиентами и менеджерами."""
    clients_list = load_clients("data/clients.json")
    managers_list = load_managers("data/managers.json")
    return load_proposals(
        "data/proposals.json",
        clients_list,
        managers_list,
    )


def _client_sum(client, proposals_list):
    """Посчитать сумму предложений одного клиента."""
    total = 0
    for proposal in proposals_list:
        if proposal.client.id == client.id:
            total += proposal.amount
    return total


def clients(request):
    """Показать список клиентов: код, название и сумма."""
    clients_list = load_clients("data/clients.json")
    proposals_list = _proposal_list()
    for client in clients_list:
        client.total_amount = _client_sum(client, proposals_list)
    context = {
        "clients": clients_list,
    }
    return render(request, "clients/client_list.html", context)


def client_detail(request, client_id):
    """Показать клиента. Если его нет — ответ 404."""
    clients_list = load_clients("data/clients.json")
    client = find_client_by_id(clients_list, client_id)
    total_amount = 0
    if client is not None:
        total_amount = _client_sum(client, _proposal_list())
    context = {
        "client": client,
        "total_amount": total_amount,
    }
    if client is None:
        return render(
            request,
            "clients/client_detail.html",
            context,
            status=404,
        )
    return render(request, "clients/client_detail.html", context)
