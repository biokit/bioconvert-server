import os
import traceback

from bioconvert.scripts import converter
from django.utils import timezone

from bioconvertapi.models import BioConvertJob
from bioconvertserver.celeryconf import app


@app.task
def compute_job(pk):
    job = BioConvertJob.objects.get(pk=pk)
    job.status = 2
    job.error_message = ""
    job.started = timezone.now()
    job.save()
    try:
        os.chdir(job.get_absolute_local_dir())
        converter.main(job.command)
        job.status = 4
    except SystemExit as e:
        if e.code == 0:
            job.status = 4
        else:
            job.status = 5
            job.error_message = traceback.format_exc()
    except Exception as e:
        job.status = 5
        job.error_message = traceback.format_exc()
    job.ended = timezone.now()
    job.save()
