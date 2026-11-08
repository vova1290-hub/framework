"""Модели менеджеров и коммерческих предложений."""

from datetime import timedelta
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Cast, Concat, Round
from django.urls import reverse


class ProposalQuerySet(models.QuerySet):
    """Повторно используемые выборки предложений."""

    def pending(self):
        return self.filter(status=Proposal.Status.PENDING)

    def approved(self):
        return self.filter(status=Proposal.Status.APPROVED)

    def cancelled(self):
        return self.filter(status=Proposal.Status.CANCELLED)

    def active(self):
        return self.exclude(status=Proposal.Status.CANCELLED)

    def with_expiration(self):
        modifier = Concat(
            models.Value("+"),
            Cast("validity_days", models.CharField()),
            models.Value(" days"),
        )
        expiration = models.Func(
            models.F("created_date"), modifier,
            function="DATE", output_field=models.DateField(),
        )
        return self.alias(expires=expiration)

    def for_date(self, selected_date):
        return self.with_expiration().filter(
            created_date__lte=selected_date, expires__gte=selected_date,
        )

    def cards(self):
        return self.with_expiration().annotate(
            client_name=models.F("client__name"),
            expiration_date=models.F("expires"),
        ).values(
            "id", "number", "client_name", "created_date",
            "expiration_date", "status",
        )

    def with_parties(self):
        return self.select_related("client", "manager")


class Manager(models.Model):
    """Менеджер, который готовит предложения."""

    name = models.CharField("Имя", max_length=255)

    class Meta:
        verbose_name = "менеджер"
        verbose_name_plural = "менеджеры"

    def __str__(self):
        return self.name


class Proposal(models.Model):
    """Коммерческое предложение для клиента."""

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает согласования"
        APPROVED = "approved", "Согласовано"
        CANCELLED = "cancelled", "Отменено"

    number = models.CharField("Номер", max_length=50, unique=True)
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        related_name="proposals",
        verbose_name="Клиент",
    )
    manager = models.ForeignKey(
        Manager,
        on_delete=models.PROTECT,
        related_name="proposals",
        verbose_name="Менеджер",
    )
    amount = models.DecimalField(
        "Сумма",
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    discount_percent = models.DecimalField(
        "Скидка, %",
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    created_date = models.DateField("Дата создания")
    validity_days = models.PositiveIntegerField(
        "Срок действия в днях",
        validators=[MinValueValidator(1)],
    )
    status = models.CharField(
        "Статус",
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    final_amount = models.GeneratedField(
        expression=Round(
            models.F("amount") * (100 - models.F("discount_percent")) / 100.0,
            precision=2,
        ),
        output_field=models.DecimalField(max_digits=14, decimal_places=2),
        db_persist=True,
        verbose_name="Итоговая сумма",
    )

    objects = ProposalQuerySet.as_manager()

    class Meta:
        verbose_name = "предложение"
        verbose_name_plural = "предложения"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="proposal_positive_amount",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    discount_percent__gte=0,
                    discount_percent__lte=100,
                ),
                name="proposal_valid_discount",
            ),
            models.CheckConstraint(
                condition=models.Q(validity_days__gt=0),
                name="proposal_positive_validity",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=[
                    "pending", "approved", "cancelled",
                ]),
                name="proposal_valid_status",
            ),
        ]

    def get_absolute_url(self):
        return reverse("proposals:detail", args=[self.pk])

    @property
    def expiration_date(self):
        """Рассчитать последний день действия предложения."""
        return self.created_date + timedelta(days=self.validity_days)

    def __str__(self):
        return self.number
