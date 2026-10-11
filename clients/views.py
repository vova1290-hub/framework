"""Страницы клиентов."""

from django.http import HttpResponse

from homepage.views import page
from models.clients import find_client_by_id
from storage import load_clients


def clients(request):
    """Показать список клиентов из JSON."""
    items = ""
    for client in load_clients("data/clients.json"):
        items += (
            '<a class="list-group-item list-group-item-action" '
            f'href="/clients/{client.id}/">{client.name}</a>'
        )
    content = f"""
<h1 class="mb-3">Клиенты</h1>
<div class="list-group shadow-sm">{items}</div>
"""
    return HttpResponse(page("Клиенты", content))


def client_detail(request, client_id):
    """Показать одного клиента. Если его нет — ответ 404."""
    clients_list = load_clients("data/clients.json")
    client = find_client_by_id(clients_list, client_id)
    if client is None:
        content = """
<div class="alert alert-danger">
    <h1 class="h4">Клиент не найден</h1>
    <a href="/clients/" class="btn btn-outline-danger">
        ← к списку клиентов
    </a>
</div>
"""
        return HttpResponse(
            page("Клиент не найден", content),
            status=404,
        )

    content = f"""
<div class="card shadow-sm">
    <div class="card-body">
        <h1 class="h4">{client.name}</h1>
        <p class="text-secondary">ID: {client.id}</p>
        <a href="/clients/" class="btn btn-outline-primary">
            ← к списку клиентов
        </a>
    </div>
</div>
"""
    return HttpResponse(page(client.name, content), status=200)
