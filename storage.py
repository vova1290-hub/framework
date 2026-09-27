"""Загрузка и сохранение данных проекта в формате JSON."""

import json
from pathlib import Path

from proposals import Proposal


def load_proposals(filename: str) -> list[Proposal]:
    """Загрузить коммерческие предложения из JSON-файла."""
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError("Файл данных содержит некорректный JSON") from error
    except OSError as error:
        raise ValueError("Не удалось прочитать файл данных") from error

    if not isinstance(data, list):
        raise ValueError("В JSON-файле должен находиться список предложений")

    return data


def save_proposals(
    filename: str,
    proposals: list[Proposal],
) -> None:
    """Сохранить коммерческие предложения в JSON-файл."""
    try:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                proposals,
                file,
                ensure_ascii=False,
                indent=2,
            )
    except OSError as error:
        raise ValueError("Не удалось сохранить файл данных") from error
