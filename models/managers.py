"""Класс менеджера и функции для работы с менеджерами."""


class Manager:
    """Менеджер, который готовит коммерческое предложение."""

    def __init__(self, manager_id: int, name: str) -> None:
        """Создать менеджера."""
        self.id = manager_id
        self.name = name

    @classmethod
    def from_data(cls, data: dict[str, object]) -> "Manager":
        """Создать менеджера из словаря с данными JSON."""
        return cls(
            int(data["id"]),
            str(data["name"]),
        )

    def __str__(self) -> str:
        """Вернуть строковое представление менеджера."""
        return f"{self.id}. {self.name}"


def add_manager(managers: list[Manager], name: str) -> Manager:
    """Создать менеджера и добавить его в коллекцию."""
    name = name.strip()
    if not name:
        raise ValueError("Имя менеджера не может быть пустым")

    manager_id = max(
        (manager.id for manager in managers),
        default=0,
    ) + 1
    manager = Manager(manager_id, name)
    managers.append(manager)
    return manager


def find_manager_by_id(
    managers: list[Manager],
    manager_id: int,
) -> Manager | None:
    """Найти менеджера по идентификатору."""
    for manager in managers:
        if manager.id == manager_id:
            return manager
    return None


def find_manager_by_name(
    managers: list[Manager],
    name: str,
) -> Manager | None:
    """Найти менеджера по точному имени."""
    normalized_name = name.strip().casefold()
    for manager in managers:
        if manager.name.casefold() == normalized_name:
            return manager
    return None
