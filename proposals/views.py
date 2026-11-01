"""Страницы коммерческих предложений."""

from django.shortcuts import render

from db.database import get_connection


def proposals(request):
    """Показать все предложения из базы SQLite."""
    connection = get_connection()
    proposals_list = connection.execute(
        """
        SELECT
            proposals.id,
            proposals.number,
            proposals.status,
            strftime('%d.%m.%Y', proposals.created_date)
                AS created_date,
            strftime(
                '%d.%m.%Y',
                date(
                    proposals.created_date,
                    '+' || proposals.validity_days || ' days'
                )
            ) AS expiration_date,
            clients.name AS client_name
        FROM proposals
        JOIN clients ON proposals.client_id = clients.id
        ORDER BY proposals.id
        """
    ).fetchall()
    connection.close()
    context = {
        "proposals": proposals_list,
    }
    return render(request, "proposals/proposal_list.html", context)


def proposal_search(request):
    """Найти предложения, которые действуют на выбранную дату."""
    selected_date = request.GET.get("date", "")
    proposals_list = []
    if selected_date:
        connection = get_connection()
        proposals_list = connection.execute(
            """
            SELECT
                proposals.id,
                proposals.number,
                proposals.status,
                strftime('%d.%m.%Y', proposals.created_date)
                    AS created_date,
                strftime(
                    '%d.%m.%Y',
                    date(
                        proposals.created_date,
                        '+' || proposals.validity_days || ' days'
                    )
                ) AS expiration_date,
                clients.name AS client_name
            FROM proposals
            JOIN clients ON proposals.client_id = clients.id
            WHERE date(?) >= date(proposals.created_date)
                AND date(?) <= date(
                    proposals.created_date,
                    '+' || proposals.validity_days || ' days'
                )
            ORDER BY proposals.id
            """,
            [selected_date, selected_date],
        ).fetchall()
        connection.close()
    context = {
        "proposals": proposals_list,
        "selected_date": selected_date,
    }
    return render(request, "proposals/proposal_search.html", context)


def proposal_statistics(request):
    """Показать, сколько предложений у каждого клиента."""
    connection = get_connection()
    clients_list = connection.execute(
        """
        SELECT
            clients.id,
            clients.name AS client_name,
            COUNT(proposals.id) AS proposals_count
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
    return render(request, "proposals/proposal_statistics.html", context)


def proposal_detail(request, proposal_id):
    """Показать одно предложение. Если его нет — ответ 404."""
    connection = get_connection()
    proposal = connection.execute(
        """
        SELECT
            proposals.id,
            proposals.number,
            proposals.status,
            ROUND(
                proposals.amount
                * (100 - proposals.discount_percent) / 100,
                2
            ) AS final_amount,
            strftime('%d.%m.%Y', proposals.created_date)
                AS created_date,
            strftime(
                '%d.%m.%Y',
                date(
                    proposals.created_date,
                    '+' || proposals.validity_days || ' days'
                )
            ) AS expiration_date,
            clients.name AS client_name,
            managers.name AS manager_name
        FROM proposals
        JOIN clients ON proposals.client_id = clients.id
        JOIN managers ON proposals.manager_id = managers.id
        WHERE proposals.id = ?
        """,
        [proposal_id],
    ).fetchone()
    connection.close()
    context = {
        "proposal": proposal,
    }
    if proposal is None:
        return render(
            request,
            "proposals/proposal_detail.html",
            context,
            status=404,
        )
    return render(request, "proposals/proposal_detail.html", context)
