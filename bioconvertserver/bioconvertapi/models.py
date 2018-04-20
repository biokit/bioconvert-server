import datetime
import json
import os
import shutil

from django.core.files.storage import default_storage
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from bioconvertserver import settings


class BioConvertJob(models.Model):
    in_fmt = models.CharField(
        max_length=32,
    )
    out_fmt = models.CharField(
        max_length=32,
    )
    identifier = models.CharField(
        max_length=32,
        validators=[MinLengthValidator(32), ],
    )
    created = models.DateTimeField(
    )
    started = models.DateTimeField(
        null=True,
        blank=True,
    )
    ended = models.DateTimeField(
        null=True,
        blank=True,
    )
    death_time = models.DateTimeField(
        null=True,
        blank=True,
    )
    command_str = models.TextField(
        default=""
    )
    status = models.IntegerField(
        choices=(
            (0, _("New")),
            (1, _("Pending")),
            (2, _("Running")),
            (4, _("Done")),
            (5, _("Error")),
            (6, _("Canceled"))
        ),
        default=0,
    )
    error_message = models.TextField(
        default="",
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk is None:
            self.identifier = get_random_string(32)
            self.created = timezone.now()
            self.revive(save=False)

    def __str__(self):
        return "Job(%s)" % self.identifier

    def get_local_dir(self):
        return os.path.join(self.identifier)

    def get_absolute_local_dir(self):
        return default_storage.path(self.identifier)

    def revive(self, save=True):
        self.death_time = datetime.datetime.now() + JobLifeLength.objects.get().life_length
        if save:
            self.save()

    def get_absolute_url(self):
        return reverse('webui:results', args=[self.identifier])

    def _get_command(self):
        return json.loads(self.command_str)

    def _set_command(self, command):
        self.command_str = json.dumps(command)

    command = property(_get_command, _set_command)

    def trigger_computation(self):
        if self.status in [0, 4, 5, 6]:
            from bioconvertapi import tasks
            self.status = 1
            self.save()
            if settings.CELERY_ENABLED:
                tasks.compute_job.delay(pk=self.pk)
            else:
                tasks.compute_job(self.pk)

    def delete(self, using=None, keep_parents=False):
        shutil.rmtree(self.get_absolute_local_dir(), ignore_errors=True)
        super().delete(using=using, keep_parents=keep_parents)


class SingletonModel:

    def clean(self):
        if self.pk is None:
            if self.__class__.objects.exists():
                raise ValidationError(
                    _('You can create at most one of it, an object already exists'),
                )
        super().clean()


class JobLifeLength(SingletonModel, models.Model):
    life_length = models.DurationField(
        null=False,
        blank=False,
    )

    def __str__(self):
        return str(self.life_length)
