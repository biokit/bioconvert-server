import datetime

from django.contrib import admin
from django.utils import formats, timezone
# Register your models here.
from django.utils.html import format_html

from bioconvertapi.models import JobLifeLength


def revive(modeladmin, request, queryset):
    for o in queryset:
        o.revive()


def trigger_computation(modeladmin, request, queryset):
    for o in queryset:
        o.trigger_computation()


def delete_selected(modeladmin, request, queryset):
    for element in queryset:
        element.delete()
delete_selected.short_description = "Delete selected elements"


class BioConvertJobAdmin(admin.ModelAdmin):
    actions = [
        delete_selected,
        revive,
        trigger_computation,
    ]
    list_display = (
        'in_fmt', 'out_fmt',
        'identifier',
        'created',
        '_death_time',
        'status'
    )
    list_display_links = list_display
    list_filter = (
        'in_fmt',
        'out_fmt',
        'status'
    )

    date_hierarchy = 'created'
    save_as = True

    def _death_time(self, obj):
        remaining_life = obj.death_time - timezone.now()
        percentage_remaining = remaining_life / JobLifeLength.objects.get().life_length
        if percentage_remaining < 0.2:
            color = "red"
        elif percentage_remaining < 0.5:
            color = "orange"
        elif percentage_remaining < 0.7:
            color = "#b3b300"
        else:
            color = "green"
        return format_html(u'<span style="color:{}">{}, {}</span>'.format(
            color,
            formats.date_format(obj.death_time),
            formats.time_format(obj.death_time),
        ))
