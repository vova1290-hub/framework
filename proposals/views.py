"""Страницы коммерческих предложений."""

from django.http import HttpResponse

from homepage.views import page
from models.proposals import Proposal, find_proposal_by_id
from storage import load_clients, load_managers, load_proposals


def badge_class(proposal: Proposal) -> str:
    """Выбрать цвет бейджа по статусу предложения."""
    if proposal.status == Proposal.STATUS_CANCELLED:
        return "bg-secondary"
    if proposal.status == Proposal.STATUS_APPROVED:
        return "bg-success"
    return "bg-warning text-dark"


def proposals(request):
    """Показать список предложений из JSON."""
    clients_list = load_clients("data/clients.json")
    managers_list = load_managers("data/managers.json")
    proposals_list = load_proposals(
        "data/proposals.json",
        clients_list,
        managers_list,
    )
    items = ""
    for proposal in proposals_list:
        badge = badge_class(proposal)
        items += (
            '<a class="list-group-item list-group-item-action '
            'd-flex flex-column flex-sm-row '
            'justify-content-sm-between '
            'align-items-sm-center gap-2" '
            f'href="/proposals/{proposal.id}/">'
            "<span>"
            f"{proposal.number} – {proposal.client.name}"
            "</span>"
            f'<span class="badge {badge} align-self-start">'
            f"{proposal.status}</span>"
            "</a>"
        )
    content = f"""
<h1 class="mb-3">Предложения</h1>
<div class="list-group shadow-sm">{items}</div>
"""
    return HttpResponse(page("Предложения", content))


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
    if proposal is None:
        content = """
<div class="alert alert-danger">
    <h1 class="h4">Предложение не найдено</h1>
    <a href="/proposals/" class="btn btn-outline-danger">
        ← к списку предложений
    </a>
</div>
"""
        return HttpResponse(
            page("Предложение не найдено", content),
            status=404,
        )

    badge = badge_class(proposal)
    created = proposal.created_date.strftime("%d.%m.%Y")
    expires = proposal.get_expiration_date().strftime("%d.%m.%Y")
    amount = f"{proposal.final_amount:.2f}"
    content = f"""
<div class="card shadow-sm">
    <div class="card-body">
        <div class="d-flex flex-wrap justify-content-between gap-2">
            <h1 class="h4 mb-0">Предложение №{proposal.id}</h1>
            <span class="badge {badge}">{proposal.status}</span>
        </div>
        <p class="display-6 mt-3 mb-0">{amount} руб.</p>
        <p class="text-secondary">Итоговая сумма</p>
        <ul class="list-group list-group-flush">
            <li class="list-group-item px-0">
                Номер: {proposal.number}
            </li>
            <li class="list-group-item px-0">
                Клиент: {proposal.client.name}
            </li>
            <li class="list-group-item px-0">
                Менеджер: {proposal.manager.name}
            </li>
            <li class="list-group-item px-0">
                Дата создания: {created}
            </li>
            <li class="list-group-item px-0">
                Действует до: {expires}
            </li>
        </ul>
        <a href="/proposals/" class="btn btn-outline-primary mt-3">
            ← к списку предложений
        </a>
    </div>
</div>
"""
    return HttpResponse(
        page(f"Предложение №{proposal.id}", content),
        status=200,
    )
