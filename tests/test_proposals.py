"""Автоматические тесты функций коммерческих предложений."""

from datetime import date

import pytest

from proposals import (
    STATUS_APPROVED,
    add_proposal,
    calculate_final_amount,
    calculate_statistics,
    change_proposal_status,
    find_proposals,
    iter_proposals_by_status,
    sort_proposals_by_amount,
)
from storage import load_proposals, save_proposals


def make_proposals() -> list[dict[str, object]]:
    """Создать небольшой набор предложений для тестов."""
    proposals: list[dict[str, object]] = []
    add_proposal(
        proposals,
        "КП-001",
        "ООО Альфа",
        150000.0,
        10.0,
        date(2026, 9, 27),
        14,
    )
    add_proposal(
        proposals,
        "КП-002",
        "ООО Вектор",
        100000.0,
        0.0,
        date(2026, 9, 28),
        30,
    )
    return proposals


def test_add_proposal_and_calculate_final_amount() -> None:
    proposals = make_proposals()

    assert len(proposals) == 2
    assert calculate_final_amount(150000.0, 10.0) == 135000.0
    assert proposals[0]["status"] == "Ожидает согласования"


def test_duplicate_proposal_number_forbidden() -> None:
    proposals = make_proposals()

    with pytest.raises(ValueError):
        add_proposal(
            proposals,
            "КП-001",
            "Новый клиент",
            50000.0,
            5.0,
            date(2026, 10, 1),
            10,
        )


def test_find_and_sort_proposals() -> None:
    proposals = make_proposals()

    found = find_proposals(proposals, "альфа")
    sorted_proposals = sort_proposals_by_amount(proposals)

    assert found == [proposals[0]]
    assert sorted_proposals[0]["number"] == "КП-002"


def test_change_status_filter_and_statistics() -> None:
    proposals = make_proposals()
    change_proposal_status(proposals, 1, STATUS_APPROVED)

    approved = list(
        iter_proposals_by_status(proposals, STATUS_APPROVED)
    )
    statistics = calculate_statistics(proposals)

    assert approved == [proposals[0]]
    assert statistics["approved_count"] == 1
    assert statistics["unique_clients_count"] == 2


def test_save_and_load_proposals(tmp_path) -> None:
    proposals = make_proposals()
    filename = tmp_path / "proposals.json"

    save_proposals(str(filename), proposals)
    loaded_proposals = load_proposals(str(filename))

    assert loaded_proposals == proposals
