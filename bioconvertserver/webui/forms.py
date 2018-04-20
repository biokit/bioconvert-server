from django import forms
from bioconvert.core.registry import Registry
from django.utils.translation import ugettext_lazy as _


class FormIdentifier(forms.Form):
    key = forms.CharField(
        initial="identifier",
        widget=forms.HiddenInput(),
    )
    identifier = forms.CharField(
        min_length=32,
        max_length=32,
        required=True,
    )


def get_format_choices(input=True):
    mapper = Registry()
    input_formats = sorted(set([k[0 if input else 1] for k in mapper.get_conversions()]))
    if input:
        yield ('AUTO', _('auto'))
    for f in input_formats:
        yield (f, f)


class FormFile(forms.Form):
    key = forms.CharField(
        initial="file",
        widget=forms.HiddenInput(),
    )
    input_file = forms.FileField(
        required=True,
        label=_("file"),
    )
    input_format = forms.ChoiceField(
        choices=get_format_choices(input=True),
        required=True,
        label=_("from"),
        initial='',
    )
    output_format = forms.ChoiceField(
        choices=get_format_choices(input=False),
        required=True,
        label=_("to"),
    )


class FormURL(forms.Form):
    key = forms.CharField(
        initial="url",
        widget=forms.HiddenInput(),
    )
    input_url = forms.URLField(
        required=True,
        label=_("URL"),
    )
    input_format = forms.ChoiceField(
        choices=get_format_choices(input=True),
        required=True,
        label=_("from"),
        initial='',
    )
    output_format = forms.ChoiceField(
        choices=get_format_choices(input=False),
        required=True,
        label=_("to"),
    )
