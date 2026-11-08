"""Модели менеджеров и коммерческих предложений."""

from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


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
        PENDING = "Ожидает согласования", "Ожидает согласования"
        APPROVED = "Согласовано", "Согласовано"
        CANCELLED = "Отменено", "Отменено"

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
                    "Ожидает согласования", "Согласовано", "Отменено",
                ]),
                name="proposal_valid_status",
            ),
        ]

    @property
    def final_amount(self):
        """Рассчитать сумму с учётом скидки."""
        amount = self.amount * (100 - self.discount_percent) / 100
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def expiration_date(self):
        """Рассчитать последний день действия предложения."""
        return self.created_date + timedelta(days=self.validity_days)

    def __str__(self):
        return self.number
