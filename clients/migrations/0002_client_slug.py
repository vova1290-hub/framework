"""Добавление постоянных адресов для существующих клиентов."""

from django.db import migrations, models

from clients.slugs import client_slug


def fill_slugs(apps, schema_editor):
    client_model = apps.get_model("clients", "Client")
    clients = client_model.objects.using(schema_editor.connection.alias)
    for client in clients.iterator():
        clients.filter(pk=client.pk).update(
            slug=client_slug(client.name, client.pk),
        )


class Migration(migrations.Migration):
    dependencies = [("clients", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="client",
            name="slug",
            field=models.SlugField(
                "Адрес", max_length=90, editable=False, null=True,
            ),
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="client",
            name="slug",
            field=models.SlugField(
                "Адрес", max_length=90, editable=False, unique=True,
            ),
        ),
    ]
