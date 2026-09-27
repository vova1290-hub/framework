"""Функции для работы с коммерческими предложениями."""

from collections.abc import Iterator
from datetime import date, timedelta

Proposal = dict[str, object]

STATUS_PENDING = "Ожидает согласования"
STATUS_APPROVED = "Согласовано"
STATUS_CANCELLED = "Отменено"
PROPOSAL_STATUSES = (
    STATUS_PENDING,
    STATUS_APPROVED,
    STATUS_CANCELLED,
)


def calculate_final_amount(
    amount: float,
    discount_percent: float,
) -> float:
    """Рассчитать итоговую сумму предложения с учётом скидки."""
    if discount_percent < 0 or discount_percent > 100:
        return amount

    discount_amount = amount * discount_percent / 100
    return amount - discount_amount


def get_proposal_status(is_approved: bool) -> str:
    """Вернуть статус коммерческого предложения."""
    if is_approved:
        return STATUS_APPROVED

    return STATUS_PENDING


def calculate_expiration_date(
    created_date: date,
    validity_days: int,
) -> date:
    """Рассчитать дату окончания действия предложения."""
    return created_date + timedelta(days=validity_days)


def is_proposal_number_available(
    proposals: list[Proposal],
    proposal_number: str,
) -> bool:
    """Проверить, свободен ли номер коммерческого предложения."""
    normalized_number = proposal_number.strip().casefold()
    return all(
        str(proposal["number"]).casefold() != normalized_number
        for proposal in proposals
    )


def add_proposal(
    proposals: list[Proposal],
    proposal_number: str,
    client_name: str,
    amount: float,
    discount_percent: float,
    created_date: date,
    validity_days: int,
) -> Proposal:
    """Проверить данные и добавить коммерческое предложение."""
    proposal_number = proposal_number.strip()
    client_name = client_name.strip()

    if not proposal_number:
        raise ValueError("Номер предложения не может быть пустым")
    if not client_name:
        raise ValueError("Название клиента не может быть пустым")
    if amount <= 0:
        raise ValueError("Сумма должна быть больше нуля")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Скидка должна находиться в диапазоне от 0 до 100")
    if validity_days <= 0:
        raise ValueError("Срок действия должен быть больше нуля")
    if not is_proposal_number_available(proposals, proposal_number):
        raise ValueError("Предложение с таким номером уже существует")

    proposal_id = max(
        (int(proposal["id"]) for proposal in proposals),
        default=0,
    ) + 1
    proposal: Proposal = {
        "id": proposal_id,
        "number": proposal_number,
        "client": client_name,
        "amount": amount,
        "discount_percent": discount_percent,
        "created_date": created_date.isoformat(),
        "validity_days": validity_days,
        "status": get_proposal_status(False),
    }
    proposals.append(proposal)
    return proposal


def find_proposals(
    proposals: list[Proposal],
    query: str,
) -> list[Proposal]:
    """Найти предложения по номеру или названию клиента."""
    normalized_query = query.strip().casefold()
    return [
        proposal
        for proposal in proposals
        if normalized_query in str(proposal["number"]).casefold()
        or normalized_query in str(proposal["client"]).casefold()
    ]


def iter_proposals_by_status(
    proposals: list[Proposal],
    status: str,
) -> Iterator[Proposal]:
    """Последовательно возвращать предложения с указанным статусом."""
    if status not in PROPOSAL_STATUSES:
        raise ValueError("Неизвестный статус предложения")

    for proposal in proposals:
        if proposal["status"] == status:
            yield proposal


def sort_proposals_by_amount(
    proposals: list[Proposal],
    reverse: bool = False,
) -> list[Proposal]:
    """Вернуть предложения, отсортированные по итоговой сумме."""
    return sorted(
        proposals,
        key=lambda proposal: calculate_final_amount(
            float(proposal["amount"]),
            float(proposal["discount_percent"]),
        ),
        reverse=reverse,
    )


def change_proposal_status(
    proposals: list[Proposal],
    proposal_id: int,
    status: str,
) -> Proposal:
    """Изменить статус предложения с указанным идентификатором."""
    if status not in PROPOSAL_STATUSES:
        raise ValueError("Неизвестный статус предложения")

    for proposal in proposals:
        if proposal["id"] == proposal_id:
            proposal["status"] = status
            return proposal

    raise ValueError("Коммерческое предложение не найдено")


def calculate_statistics(
    proposals: list[Proposal],
) -> dict[str, object]:
    """Рассчитать сводную статистику по предложениям."""
    active_proposals = [
        proposal
        for proposal in proposals
        if proposal["status"] != STATUS_CANCELLED
    ]
    total_amount = sum(
        calculate_final_amount(
            float(proposal["amount"]),
            float(proposal["discount_percent"]),
        )
        for proposal in active_proposals
    )
    average_amount = (
        total_amount / len(active_proposals)
        if active_proposals
        else 0.0
    )
    unique_clients = {
        str(proposal["client"])
        for proposal in proposals
    }

    return {
        "total_count": len(proposals),
        "active_count": len(active_proposals),
        "approved_count": sum(
            proposal["status"] == STATUS_APPROVED
            for proposal in proposals
        ),
        "unique_clients_count": len(unique_clients),
        "total_amount": total_amount,
        "average_amount": average_amount,
    }
