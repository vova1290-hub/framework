"""Класс клиента и функции для работы с клиентами."""


class Client:
    """Клиент, для которого готовится коммерческое предложение."""

    def __init__(self, client_id: int, name: str) -> None:
        """Создать клиента."""
        self.id = client_id
        self.name = name

    @classmethod
    def from_data(cls, data: dict[str, object]) -> "Client":
        """Создать клиента из словаря с данными JSON."""
        return cls(
            int(data["id"]),
            str(data["name"]),
        )

    def __str__(self) -> str:
        """Вернуть строковое представление клиента."""
        return f"{self.id}. {self.name}"


def add_client(clients: list[Client], name: str) -> Client:
    """Создать клиента и добавить его в коллекцию."""
    name = name.strip()
    if not name:
        raise ValueError("Название клиента не может быть пустым")

    client_id = max(
        (client.id for client in clients),
        default=0,
    ) + 1
    client = Client(client_id, name)
    clients.append(client)
    return client


def find_client_by_id(
    clients: list[Client],
    client_id: int,
) -> Client | None:
    """Найти клиента по идентификатору."""
    for client in clients:
        if client.id == client_id:
            return client
    return None


def find_client_by_name(
    clients: list[Client],
    name: str,
) -> Client | None:
    """Найти клиента по точному названию."""
    normalized_name = name.strip().casefold()
    for client in clients:
        if client.name.casefold() == normalized_name:
            return client
    return None
