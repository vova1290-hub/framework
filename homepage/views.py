"""Главная страница."""

from django.shortcuts import render


def index(request):
    """Показать главную страницу."""
    return render(request, "homepage/index.html")


def page_not_found(request, exception):
    """Показать страницу, если адрес не найден."""
    return render(request, "404.html", status=404)
