"""Страницы коммерческих предложений."""

from django.shortcuts import render

from models.proposals import find_proposal_by_id
from storage import load_clients, load_managers, load_proposals


def proposals(request):
    """Показать список предложений из JSON."""
    clients_list = load_clients("data/clients.json")
    managers_list = load_managers("data/managers.json")
    proposals_list = load_proposals(
        "data/proposals.json",
        clients_list,
        managers_list,
    )
    context = {
        "proposals": proposals_list,
    }
    return render(request, "proposals/proposal_list.html", context)


def proposal_detail(request, proposal_id):
    """Показать одно предложение. Если его нет — ответ 404."""
    clients_list = load_clients("data/clients.json")
    managers_list = load_managers("data/managers.json")
    proposals_list = load_proposals(
        "data/proposals.json",
        clients_list,
        managers_list,
    )
    proposal = find_proposal_by_id(proposals_list, proposal_id)
    context = {
        "proposal": proposal,
    }
    if proposal is None:
        return render(
            request,
            "proposals/proposal_detail.html",
            context,
            status=404,
        )
    return render(request, "proposals/proposal_detail.html", context)
