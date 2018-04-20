from django.contrib import admin

from bioconvertapi.admin.bio_convert_job import BioConvertJobAdmin
from bioconvertapi.models import BioConvertJob, JobLifeLength

# Register your models here.

admin.site.register(JobLifeLength)
admin.site.register(BioConvertJob, BioConvertJobAdmin)
