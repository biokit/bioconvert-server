import itertools
import json
import os

from bioconvert.core.base import ConvArg
from bioconvert.core.registry import Registry
from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from urllib import request as urllib_request
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from bioconvertapi.models import BioConvertJob


class BioconvertJobForm(forms.Form):
    mapper = Registry(including_not_available_converter=True)
    black_listed_arg_name = [
        '--verbosity',
        '--force',
        '--batch',
        '--benchmark-N',
        '--benchmark',
        '--show-methods',
        '--raise-exception',
        '--allow-indirect-conversion',
        # 'output_file',
    ]

    def __init__(self,
                 in_fmt,
                 out_fmt,
                 black_listed_argument_name = None,
                 *args,
                 **kwargs):

        super().__init__(*args, **kwargs)
        self.in_fmt = in_fmt.upper()
        self.out_fmt = out_fmt.upper()
        self.class_converter = self.mapper[(self.in_fmt, self.out_fmt)]
        self.file_url_choosers = []
        for arg in itertools.chain(
                self.class_converter.get_common_arguments_for_converter(),
                self.class_converter.get_additional_arguments(),
        ):
            raw_arg_name = sorted(arg.args_for_sub_parser)[0]
            if raw_arg_name in self.black_listed_arg_name:
                continue
            if raw_arg_name in (black_listed_argument_name or []):
                continue

            arg_help = arg.kwargs_for_sub_parser.get("help", None)
            arg_type = arg.kwargs_for_sub_parser.get("type", str)
            arg_default = arg.kwargs_for_sub_parser.get("default", None)
            arg_nargs = arg.kwargs_for_sub_parser.get("nargs", None)
            arg_is_output_argument = arg.kwargs_for_sub_parser.get("output_argument", None)
            if raw_arg_name == "input_file":
                arg_nargs = "1"

            arg_name = self.clean_arg_name(raw_arg_name)
            required = arg_nargs is None or arg_nargs != "?"

            if arg_type is int:
                self.fields[arg_name] = forms.IntegerField(
                    help_text=arg_help,
                    required=required,
                )
            elif arg_type is bool:
                self.fields[arg_name] = forms.BooleanField(
                    help_text=arg_help,
                )
            elif arg_type is str or \
                    arg_type == ConvArg.file and arg_is_output_argument:
                # filename in ouput ar considered as string as they will be relative path to job dir
                arg_choices = arg.kwargs_for_sub_parser.get("choices", None)
                if arg_choices:
                    self.fields[arg_name] = forms.ChoiceField(
                        choices=[(c, c) for c in arg_choices],
                        help_text=arg_help,
                        required=required,
                    )
                else:
                    self.fields[arg_name] = forms.CharField(
                        help_text=arg_help,
                        required=required,
                    )
                    if arg_default:
                        arg_default = repr(arg_default)[1:-1]
                    # fields[arg_name].widget = forms.Textarea()
            elif arg_type == ConvArg.file:
                # A file (in input) can also be a url, so duplicating the field and adding a radio to choose
                if "_file" in arg_name:
                    arg_name = arg_name.replace("_file", "")
                selected = self.__is_selected_in_data_when_provided(arg_name, "file", default=False, **kwargs)
                self.fields[arg_name + "_file"] = forms.FileField(
                    help_text=arg_help,
                    required=required and selected,
                    disabled=not selected,
                )
                selected = self.__is_selected_in_data_when_provided(arg_name, "url", default=True, **kwargs)
                self.fields[arg_name + "_url"] = forms.URLField(
                    help_text=arg_help,
                    required=required and selected,
                    disabled=not selected,
                )
                self.fields[arg_name + "_type"] = forms.ChoiceField(
                    choices=[("file", _("File")), ("url", _("URL")), ],
                    help_text=arg_help,
                    widget=widgets.RadioSelect(attrs={
                        'display': 'inline-block'
                    }),
                    required=True,
                    initial="url",
                )
                self.file_url_choosers.append(arg_name + "_type")
            else:
                print("Unhandeld type " + str(arg_type))
                continue
            if arg_default:
                self.fields[arg_name].initial = arg_default

    @staticmethod
    def clean_arg_name(arg_name):
        return arg_name.replace("-", "_").replace("__", "")

    @staticmethod
    def __is_selected_in_data_when_provided(arg_name, value, default, data=None, *args, **kwargs):
        if data is None:
            return default
        try:
            return data[arg_name + "_type"] == value
        except Exception as e:
            print(e)
            return False

    def save(self):
        job = BioConvertJob(in_fmt=self.in_fmt, out_fmt=self.out_fmt)
        print(self.cleaned_data)

        # Saving inputs files
        for name in self.file_url_choosers:
            name_file = name[:-4] + "file"
            name_url = name[:-4] + "url"
            print(name)
            if self.cleaned_data[name] == "file":
                # it's a file, get the content from memory
                input_filename = self.cleaned_data[name_file].name
                content = self.cleaned_data[name_file].read()
            elif self.cleaned_data[name] == "url":
                # it's a URL, download the content
                input_filename = self.cleaned_data[name_url][self.cleaned_data[name_url].rindex('/') + 1:]
                response = urllib_request.urlretrieve(self.cleaned_data[name_url])
                content = open(response[0]).read()
            else:
                continue
            # Find where the file will be saved
            in_media_path = os.path.join(job.get_local_dir(), input_filename)
            default_storage.save(in_media_path, ContentFile(content))
            self.cleaned_data[name_file] = default_storage.path(in_media_path)

        # print(self.cleaned_data)
        command = ["{}2{}".format(self.in_fmt.lower(), self.out_fmt.lower()), ]

        # Building command as it was typed
        for arg in itertools.chain(
                self.class_converter.get_common_arguments_for_converter(),
                self.class_converter.get_additional_arguments(),
        ):
            raw_arg_name = sorted(arg.args_for_sub_parser)[0]
            if raw_arg_name in self.black_listed_arg_name:
                continue
            arg_name = self.clean_arg_name(raw_arg_name)
            if self.cleaned_data[arg_name] is not None and self.cleaned_data[arg_name] != "":
                if raw_arg_name.startswith("-"):
                    command.append(raw_arg_name)
                command.append(str(self.cleaned_data[arg_name]))

        command.append("--force")

        job.command = command

        job.save()
        return job
