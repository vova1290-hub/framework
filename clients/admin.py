"""Клиенты в панели администратора."""

from django.contrib import admin

from .models import Client

admin.site.register(Client)
