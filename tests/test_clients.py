"""Автоматические тесты клиентов."""

import pytest

from models.clients import Client, add_client, find_client_by_name
from storage import load_clients, save_clients


def test_client_creation() -> None:
    client = Client(1, "ООО Альфа")

    assert client.id == 1
    assert client.name == "ООО Альфа"
    assert str(client) == "1. ООО Альфа"


def test_client_from_data() -> None:
    client = Client.from_data({
        "id": 2,
        "name": "ООО Вектор",
    })

    assert client.id == 2
    assert client.name == "ООО Вектор"


def test_add_client_and_find_by_name() -> None:
    clients: list[Client] = []
    added = add_client(clients, "ИП Смирнов")

    found = find_client_by_name(clients, "ип смирнов")

    assert found is added
    assert len(clients) == 1


def test_empty_client_name() -> None:
    with pytest.raises(ValueError):
        add_client([], "   ")


def test_save_and_load_clients(tmp_path) -> None:
    clients = [Client(1, "ООО Альфа")]
    filename = tmp_path / "clients.json"

    save_clients(str(filename), clients)
    loaded_clients = load_clients(str(filename))

    assert len(loaded_clients) == 1
    assert loaded_clients[0].id == 1
    assert loaded_clients[0].name == "ООО Альфа"


def test_load_missing_and_invalid_file(tmp_path) -> None:
    missing = tmp_path / "missing.json"
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")

    assert load_clients(str(missing)) == []
    with pytest.raises(ValueError):
        load_clients(str(invalid))
