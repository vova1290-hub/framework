"""Модель клиента."""

from django.db import models


class Client(models.Model):
    """Организация, для которой создаются предложения."""

    name = models.CharField("Название", max_length=255)

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"

    def __str__(self):
        return self.name
