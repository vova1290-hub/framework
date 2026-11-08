"""Общие данные шаблонов."""

from proposals.models import Proposal


def project(request):
    return {
        "site_name": "Учёт КП",
        "proposal_status": Proposal.Status,
    }
