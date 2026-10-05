"""Автоматические тесты коммерческих предложений."""

from datetime import date

import pytest

from models.clients import Client, add_client
from models.managers import Manager, add_manager
from models.proposals import (
    Proposal,
    add_proposal,
    calculate_statistics,
    change_proposal_status,
    find_proposals,
    iter_proposals_by_status,
    sort_proposals_by_amount,
)
from storage import load_proposals, save_proposals


def make_data() -> tuple[list[Client], list[Manager], list[Proposal]]:
    """Создать клиентов, менеджеров и предложения для тестов."""
    clients: list[Client] = []
    managers: list[Manager] = []
    alpha = add_client(clients, "ООО Альфа")
    vector = add_client(clients, "ООО Вектор")
    ivanov = add_manager(managers, "Иванов Иван")
    petrova = add_manager(managers, "Петрова Анна")
    proposals: list[Proposal] = []
    add_proposal(
        proposals,
        "КП-001",
        alpha,
        ivanov,
        150000.0,
        10.0,
        date(2026, 9, 27),
        14,
    )
    add_proposal(
        proposals,
        "КП-002",
        vector,
        petrova,
        100000.0,
        0.0,
        date(2026, 9, 28),
        30,
    )
    return clients, managers, proposals


def test_proposal_creation() -> None:
    clients, managers, proposals = make_data()
    proposal = proposals[0]

    assert proposal.id == 1
    assert proposal.number == "КП-001"
    assert proposal.client is clients[0]
    assert proposal.manager is managers[0]
    assert proposal.amount == 150000.0
    assert proposal.discount_percent == 10.0
    assert proposal.final_amount == 135000.0
    assert proposal.get_expiration_date() == date(2026, 10, 11)
    assert proposal.status == Proposal.STATUS_PENDING
    assert str(proposal) == (
        "1. КП-001 | ООО Альфа | Иванов Иван | "
        "135000.00 руб. | до 11.10.2026 | Ожидает согласования"
    )
    assert Proposal.validate_discount(10.0)
    assert not Proposal.validate_discount(120.0)


def test_add_proposal_and_calculate_final_amount() -> None:
    _, _, proposals = make_data()

    assert len(proposals) == 2
    assert proposals[0].final_amount == 135000.0
    assert proposals[0].status == "Ожидает согласования"


def test_duplicate_proposal_number_forbidden() -> None:
    _, _, proposals = make_data()

    with pytest.raises(ValueError):
        add_proposal(
            proposals,
            "КП-001",
            proposals[0].client,
            proposals[0].manager,
            50000.0,
            5.0,
            date(2026, 10, 1),
            10,
        )


def test_invalid_discount() -> None:
    _, _, proposals = make_data()

    with pytest.raises(ValueError):
        add_proposal(
            proposals,
            "КП-003",
            proposals[0].client,
            proposals[0].manager,
            50000.0,
            150.0,
            date(2026, 10, 1),
            10,
        )


def test_find_and_sort_proposals() -> None:
    _, _, proposals = make_data()

    found = find_proposals(proposals, "альфа")
    sorted_proposals = sort_proposals_by_amount(proposals)

    assert found == [proposals[0]]
    assert sorted_proposals[0].number == "КП-002"


def test_change_status_filter_and_statistics() -> None:
    _, _, proposals = make_data()
    change_proposal_status(
        proposals,
        1,
        Proposal.STATUS_APPROVED,
    )

    approved = list(
        iter_proposals_by_status(
            proposals,
            Proposal.STATUS_APPROVED,
        )
    )
    statistics = calculate_statistics(proposals)

    assert approved == [proposals[0]]
    assert proposals[0].status == Proposal.STATUS_APPROVED
    assert statistics["approved_count"] == 1
    assert statistics["active_count"] == 2
    assert statistics["unique_clients_count"] == 2


def test_cancel_keeps_proposal() -> None:
    _, _, proposals = make_data()
    change_proposal_status(
        proposals,
        1,
        Proposal.STATUS_CANCELLED,
    )
    statistics = calculate_statistics(proposals)

    assert len(proposals) == 2
    assert proposals[0].status == Proposal.STATUS_CANCELLED
    assert not proposals[0].is_active()
    assert statistics["active_count"] == 1
    assert statistics["total_count"] == 2


def test_two_proposals_for_one_client_and_manager() -> None:
    clients: list[Client] = []
    managers: list[Manager] = []
    client = add_client(clients, "ООО Альфа")
    manager = add_manager(managers, "Иванов Иван")
    proposals: list[Proposal] = []
    first = add_proposal(
        proposals,
        "КП-010",
        client,
        manager,
        10000.0,
        0.0,
        date(2026, 10, 1),
        7,
    )
    second = add_proposal(
        proposals,
        "КП-011",
        client,
        manager,
        20000.0,
        0.0,
        date(2026, 10, 2),
        7,
    )
    statistics = calculate_statistics(proposals)

    assert first.client is client
    assert second.client is client
    assert first.manager is manager
    assert second.manager is manager
    assert statistics["unique_clients_count"] == 1
    assert statistics["total_count"] == 2


def test_missing_proposal() -> None:
    _, _, proposals = make_data()

    with pytest.raises(ValueError):
        change_proposal_status(
            proposals,
            99,
            Proposal.STATUS_APPROVED,
        )


def test_save_and_load_proposals(tmp_path) -> None:
    clients, managers, proposals = make_data()
    filename = tmp_path / "proposals.json"

    save_proposals(str(filename), proposals)
    loaded_proposals = load_proposals(str(filename), clients, managers)

    assert loaded_proposals[0].number == proposals[0].number
    assert loaded_proposals[0].amount == proposals[0].amount
    assert loaded_proposals[0].client is clients[0]
    assert loaded_proposals[0].manager is managers[0]
    assert loaded_proposals[0].status == proposals[0].status
    assert loaded_proposals[1].client is clients[1]
    assert loaded_proposals[1].manager is managers[1]


def test_load_proposal_without_client(tmp_path) -> None:
    filename = tmp_path / "proposals.json"
    filename.write_text(
        """
        [{
          "id": 1,
          "number": "КП-001",
          "client_id": 99,
          "manager_id": 1,
          "amount": 1000,
          "discount_percent": 0,
          "created_date": "2026-10-01",
          "validity_days": 5,
          "status": "Ожидает согласования"
        }]
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_proposals(str(filename), [], [])
