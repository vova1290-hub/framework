"""Маршруты коммерческих предложений."""

from django.urls import path

from . import views

app_name = "proposals"

urlpatterns = [
    path("", views.proposals, name="list"),
    path(
        "<int:proposal_id>/",
        views.proposal_detail,
        name="detail",
    ),
]
