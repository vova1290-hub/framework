"""Маршруты клиентов."""

from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    path("", views.clients, name="list"),
    path("<int:client_id>/", views.client_detail, name="detail"),
]
