from __future__ import unicode_literals

from datetime import timedelta

from django.db import migrations


def migration_code(apps, schema_editor):
    JobLifeLength = apps.get_model("bioconvertapi", "JobLifeLength")
    if not JobLifeLength.objects.exists():
        JobLifeLength.objects.create(life_length=timedelta(days=7))


def reverse_code(apps, schema_editor):
    JobLifeLength = apps.get_model("bioconvertapi", "JobLifeLength")
    JobLifeLength.objects.get().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('bioconvertapi', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migration_code, reverse_code=reverse_code),
    ]
