"""Главная страница и общий каркас HTML."""

from django.http import HttpResponse


def page(title, content):
    """Собрать HTML-страницу: Bootstrap, меню и содержимое."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body class="bg-light">
<header class="bg-primary mb-4">
    <div class="container py-3 d-flex flex-wrap align-items-center gap-3">
        <a class="text-white text-decoration-none fw-bold fs-5" href="/">
            Учёт КП
        </a>
        <a class="text-white text-decoration-none" href="/">Главная</a>
        <a class="text-white text-decoration-none" href="/clients/">
            Клиенты
        </a>
        <a class="text-white text-decoration-none" href="/proposals/">
            Предложения
        </a>
    </div>
</header>
<main class="container pb-4">{content}</main>
</body>
</html>"""


def index(request):
    """Показать главную страницу."""
    content = """
<h1 class="mb-2">Коммерческие предложения</h1>
<p class="lead text-secondary">
    Система учёта коммерческих предложений.
</p>
<div class="row g-3">
    <div class="col-md-6">
        <div class="card h-100 shadow-sm">
            <div class="card-body">
                <h2 class="h5">Клиенты</h2>
                <p>Компании, для которых готовятся предложения.</p>
                <a href="/clients/" class="btn btn-primary">
                    Открыть список
                </a>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card h-100 shadow-sm">
            <div class="card-body">
                <h2 class="h5">Предложения</h2>
                <p>Номера, суммы, сроки и статусы.</p>
                <a href="/proposals/" class="btn btn-primary">
                    Открыть список
                </a>
            </div>
        </div>
    </div>
</div>
"""
    return HttpResponse(page("Коммерческие предложения", content))


def page_not_found(request, exception):
    """Показать страницу, если адрес не найден."""
    content = """
<div class="text-center py-5">
    <h1 class="display-4 text-danger">404</h1>
    <p class="lead">Страница не найдена</p>
    <p>Проверьте адрес или вернитесь на главную.</p>
    <a href="/" class="btn btn-primary">На главную</a>
</div>
"""
    return HttpResponse(
        page("404 – страница не найдена", content),
        status=404,
    )
