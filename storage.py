"""Загрузка и сохранение данных проекта в формате JSON."""

import json
from datetime import date
from pathlib import Path

from models.clients import Client, find_client_by_id
from models.proposals import Proposal


def _read_list(filename: str) -> list[object]:
    """Прочитать JSON-файл и вернуть список записей."""
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(
            "Файл данных содержит некорректный JSON"
        ) from error
    except OSError as error:
        raise ValueError("Не удалось прочитать файл данных") from error

    if not isinstance(data, list):
        raise ValueError("В JSON-файле должен находиться список")

    return data


def _write_list(filename: str, data: list[object]) -> None:
    """Записать список записей в JSON-файл."""
    try:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )
    except OSError as error:
        raise ValueError("Не удалось сохранить файл данных") from error


def load_clients(filename: str) -> list[Client]:
    """Загрузить клиентов и создать объекты Client."""
    clients: list[Client] = []
    for item in _read_list(filename):
        if not isinstance(item, dict):
            raise ValueError("Некорректная запись клиента")
        clients.append(Client.from_data(item))
    return clients


def save_clients(filename: str, clients: list[Client]) -> None:
    """Сохранить клиентов в JSON-файл."""
    data: list[object] = []
    for client in clients:
        data.append({
            "id": client.id,
            "name": client.name,
        })
    _write_list(filename, data)


def load_proposals(
    filename: str,
    clients: list[Client],
) -> list[Proposal]:
    """Загрузить предложения и связать их с клиентами."""
    proposals: list[Proposal] = []
    for item in _read_list(filename):
        if not isinstance(item, dict):
            raise ValueError("Некорректная запись предложения")

        client = find_client_by_id(
            clients,
            int(item["client_id"]),
        )
        if client is None:
            raise ValueError(
                "Для предложения не найден клиент "
                f"с id {item['client_id']}"
            )

        proposal = Proposal(
            int(item["id"]),
            str(item["number"]),
            client,
            float(item["amount"]),
            float(item["discount_percent"]),
            date.fromisoformat(str(item["created_date"])),
            int(item["validity_days"]),
            str(item["status"]),
        )
        proposals.append(proposal)
    return proposals


def save_proposals(
    filename: str,
    proposals: list[Proposal],
) -> None:
    """Сохранить предложения, подставив id клиента."""
    data: list[object] = []
    for proposal in proposals:
        data.append({
            "id": proposal.id,
            "number": proposal.number,
            "client_id": proposal.client.id,
            "amount": proposal.amount,
            "discount_percent": proposal.discount_percent,
            "created_date": proposal.created_date.isoformat(),
            "validity_days": proposal.validity_days,
            "status": proposal.status,
        })
    _write_list(filename, data)
