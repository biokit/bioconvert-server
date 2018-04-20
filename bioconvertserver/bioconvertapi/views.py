from django.shortcuts import render, redirect

# Create your views here.
from bioconvertapi.forms import BioconvertJobForm


def convert(request, in_fmt, out_fmt, form=None):
    if form is None:
        form = BioconvertJobForm(
            in_fmt=in_fmt,
            out_fmt=out_fmt,
            data=request.POST,
            files=request.FILES,
        )
    job = form.save()
    return redirect('webui:results', identifier=job.identifier)
