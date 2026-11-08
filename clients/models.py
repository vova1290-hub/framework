"""Модель клиента."""

from uuid import uuid4

from django.db import models
from django.urls import reverse

from .slugs import client_slug


class Client(models.Model):
    """Организация, для которой создаются предложения."""

    name = models.CharField("Название", max_length=255)

    slug = models.SlugField(
        "Адрес", max_length=90, unique=True, editable=False,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = client_slug(self.name, uuid4().hex)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("clients:by_slug", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"

    def __str__(self):
        return self.name
