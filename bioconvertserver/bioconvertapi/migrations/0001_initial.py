# Generated by Django 2.0.4 on 2018-04-20 13:35

import bioconvertapi.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BioConvertJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_fmt', models.CharField(max_length=32)),
                ('out_fmt', models.CharField(max_length=32)),
                ('identifier', models.CharField(max_length=32, validators=[django.core.validators.MinLengthValidator(32)])),
                ('created', models.DateTimeField()),
                ('death_time', models.DateTimeField(blank=True, null=True)),
                ('command_str', models.TextField(default='')),
                ('status', models.IntegerField(choices=[(0, 'New'), (1, 'Pending'), (2, 'Running'), (4, 'Done'), (5, 'Error'), (6, 'Canceled')], default=0)),
                ('error_message', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='JobLifeLength',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('life_length', models.DurationField()),
            ],
            bases=(bioconvertapi.models.SingletonModel, models.Model),
        ),
    ]