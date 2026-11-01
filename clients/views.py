"""Страницы клиентов."""

from django.shortcuts import render

from db.database import get_connection


def clients(request):
    """Показать список клиентов из базы SQLite."""
    connection = get_connection()
    clients_list = connection.execute(
        """
        SELECT
            clients.id,
            clients.name,
            COALESCE(SUM(proposals.amount), 0) AS total_amount
        FROM clients
        LEFT JOIN proposals
            ON proposals.client_id = clients.id
        GROUP BY clients.id, clients.name
        ORDER BY clients.id
        """
    ).fetchall()
    connection.close()
    context = {
        "clients": clients_list,
    }
    return render(request, "clients/client_list.html", context)


def client_detail(request, client_id):
    """Показать клиента. Если его нет — ответ 404."""
    connection = get_connection()
    client = connection.execute(
        """
        SELECT
            clients.id,
            clients.name,
            COALESCE(SUM(proposals.amount), 0) AS total_amount
        FROM clients
        LEFT JOIN proposals
            ON proposals.client_id = clients.id
        WHERE clients.id = ?
        GROUP BY clients.id, clients.name
        """,
        [client_id],
    ).fetchone()
    connection.close()
    context = {
        "client": client,
    }
    if client is None:
        return render(
            request,
            "clients/client_detail.html",
            context,
            status=404,
        )
    return render(request, "clients/client_detail.html", context)
