"""Автоматические тесты менеджеров."""

import pytest

from models.managers import Manager, add_manager, find_manager_by_name
from storage import load_managers, save_managers


def test_manager_creation() -> None:
    manager = Manager(1, "Иванов Иван")

    assert manager.id == 1
    assert manager.name == "Иванов Иван"
    assert str(manager) == "1. Иванов Иван"


def test_manager_from_data() -> None:
    manager = Manager.from_data({
        "id": 2,
        "name": "Петрова Анна",
    })

    assert manager.id == 2
    assert manager.name == "Петрова Анна"


def test_add_manager_and_find_by_name() -> None:
    managers: list[Manager] = []
    added = add_manager(managers, "Иванов Иван")

    found = find_manager_by_name(managers, "иванов иван")

    assert found is added
    assert len(managers) == 1


def test_empty_manager_name() -> None:
    with pytest.raises(ValueError):
        add_manager([], "   ")


def test_save_and_load_managers(tmp_path) -> None:
    managers = [Manager(1, "Иванов Иван")]
    filename = tmp_path / "managers.json"

    save_managers(str(filename), managers)
    loaded_managers = load_managers(str(filename))

    assert len(loaded_managers) == 1
    assert loaded_managers[0].id == 1
    assert loaded_managers[0].name == "Иванов Иван"
