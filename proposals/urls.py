"""Маршруты коммерческих предложений."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.proposals, name="proposals"),
    path(
        "<int:proposal_id>/",
        views.proposal_detail,
        name="proposal_detail",
    ),
]
