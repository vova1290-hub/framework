"""Перенос клиентов, менеджеров и предложений из JSON в SQLite."""

import sqlite3

from db.database import DB_PATH
from storage import load_clients, load_managers, load_proposals


def main():
    """Создать таблицы заново и записать в них данные из JSON."""
    schema_path = DB_PATH.parent.parent / "sql" / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(schema)

    clients = load_clients("data/clients.json")
    managers = load_managers("data/managers.json")
    proposals = load_proposals(
        "data/proposals.json",
        clients,
        managers,
    )

    connection.executemany(
        "INSERT INTO clients (id, name) VALUES (?, ?)",
        [(client.id, client.name) for client in clients],
    )
    connection.executemany(
        "INSERT INTO managers (id, name) VALUES (?, ?)",
        [(manager.id, manager.name) for manager in managers],
    )
    connection.executemany(
        """
        INSERT INTO proposals (
            id,
            number,
            client_id,
            manager_id,
            amount,
            discount_percent,
            created_date,
            validity_days,
            status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                proposal.id,
                proposal.number,
                proposal.client.id,
                proposal.manager.id,
                proposal.amount,
                proposal.discount_percent,
                proposal.created_date.isoformat(),
                proposal.validity_days,
                proposal.status,
            )
            for proposal in proposals
        ],
    )
    connection.commit()
    connection.close()


if __name__ == "__main__":
    main()
