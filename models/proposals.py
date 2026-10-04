"""Класс коммерческого предложения и функции работы с ним."""

from collections.abc import Iterator
from datetime import date, timedelta

from .clients import Client


class Proposal:
    """Коммерческое предложение для клиента."""

    STATUS_PENDING = "Ожидает согласования"
    STATUS_APPROVED = "Согласовано"
    STATUS_CANCELLED = "Отменено"
    STATUSES = (
        STATUS_PENDING,
        STATUS_APPROVED,
        STATUS_CANCELLED,
    )

    def __init__(
        self,
        proposal_id: int,
        number: str,
        client: Client,
        amount: float,
        discount_percent: float,
        created_date: date,
        validity_days: int,
        status: str = STATUS_PENDING,
    ) -> None:
        """Создать коммерческое предложение."""
        self.id = proposal_id
        self.number = number
        self.client = client
        self.amount = amount
        self.discount_percent = discount_percent
        self.created_date = created_date
        self.validity_days = validity_days
        self.status = status

    @staticmethod
    def validate_discount(discount_percent: float) -> bool:
        """Проверить, что скидка находится в диапазоне от 0 до 100."""
        return 0 <= discount_percent <= 100

    @property
    def final_amount(self) -> float:
        """Рассчитать итоговую сумму предложения с учётом скидки."""
        discount_amount = self.amount * self.discount_percent / 100
        return self.amount - discount_amount

    def get_expiration_date(self) -> date:
        """Рассчитать дату окончания срока действия."""
        return self.created_date + timedelta(days=self.validity_days)

    def is_active(self) -> bool:
        """Проверить, что предложение не отменено."""
        return self.status != self.STATUS_CANCELLED

    def set_status(self, status: str) -> None:
        """Изменить статус предложения."""
        if status not in self.STATUSES:
            raise ValueError("Неизвестный статус предложения")
        self.status = status

    def __str__(self) -> str:
        """Вернуть строковое представление предложения."""
        expiration_date = self.get_expiration_date()
        return (
            f"{self.id}. {self.number} | {self.client.name} | "
            f"{self.final_amount:.2f} руб. | "
            f"до {expiration_date:%d.%m.%Y} | {self.status}"
        )


def is_proposal_number_available(
    proposals: list[Proposal],
    proposal_number: str,
) -> bool:
    """Проверить, свободен ли номер коммерческого предложения."""
    normalized_number = proposal_number.strip().casefold()
    return all(
        proposal.number.casefold() != normalized_number
        for proposal in proposals
    )


def add_proposal(
    proposals: list[Proposal],
    proposal_number: str,
    client: Client,
    amount: float,
    discount_percent: float,
    created_date: date,
    validity_days: int,
) -> Proposal:
    """Проверить данные и добавить коммерческое предложение."""
    proposal_number = proposal_number.strip()

    if not proposal_number:
        raise ValueError("Номер предложения не может быть пустым")
    if amount <= 0:
        raise ValueError("Сумма должна быть больше нуля")
    if not Proposal.validate_discount(discount_percent):
        raise ValueError(
            "Скидка должна находиться в диапазоне от 0 до 100"
        )
    if validity_days <= 0:
        raise ValueError("Срок действия должен быть больше нуля")
    if not is_proposal_number_available(proposals, proposal_number):
        raise ValueError("Предложение с таким номером уже существует")

    proposal_id = max(
        (proposal.id for proposal in proposals),
        default=0,
    ) + 1
    proposal = Proposal(
        proposal_id,
        proposal_number,
        client,
        amount,
        discount_percent,
        created_date,
        validity_days,
    )
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
        if normalized_query in proposal.number.casefold()
        or normalized_query in proposal.client.name.casefold()
    ]


def iter_proposals_by_status(
    proposals: list[Proposal],
    status: str,
) -> Iterator[Proposal]:
    """Последовательно возвращать предложения с указанным статусом."""
    if status not in Proposal.STATUSES:
        raise ValueError("Неизвестный статус предложения")

    for proposal in proposals:
        if proposal.status == status:
            yield proposal


def sort_proposals_by_amount(
    proposals: list[Proposal],
    reverse: bool = False,
) -> list[Proposal]:
    """Вернуть предложения, отсортированные по итоговой сумме."""
    return sorted(
        proposals,
        key=lambda proposal: proposal.final_amount,
        reverse=reverse,
    )


def change_proposal_status(
    proposals: list[Proposal],
    proposal_id: int,
    status: str,
) -> Proposal:
    """Найти предложение и изменить его статус."""
    for proposal in proposals:
        if proposal.id == proposal_id:
            proposal.set_status(status)
            return proposal

    raise ValueError("Коммерческое предложение не найдено")


def calculate_statistics(
    proposals: list[Proposal],
) -> dict[str, object]:
    """Рассчитать сводную статистику по предложениям."""
    active_proposals = [
        proposal
        for proposal in proposals
        if proposal.is_active()
    ]
    total_amount = sum(
        proposal.final_amount
        for proposal in active_proposals
    )
    average_amount = (
        total_amount / len(active_proposals)
        if active_proposals
        else 0.0
    )
    unique_clients = {
        proposal.client.id
        for proposal in proposals
    }

    return {
        "total_count": len(proposals),
        "active_count": len(active_proposals),
        "approved_count": sum(
            proposal.status == Proposal.STATUS_APPROVED
            for proposal in proposals
        ),
        "unique_clients_count": len(unique_clients),
        "total_amount": total_amount,
        "average_amount": average_amount,
    }
