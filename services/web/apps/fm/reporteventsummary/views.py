# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Event Summary Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django import forms
# NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.eventclass import EventClass
from noc.fm.models.failedevent import FailedEvent
from noc.fm.models.archivedevent import ArchivedEvent
from noc.core.translation import ugettext as _

# Report types
report_types = [
    ("class", _("By Event Class")),
    ("object", _("By Managed Object")),
    ("profile", _("By Profile")),
    ("status", _("By Status"))
]


class ReportForm(forms.Form):
    report_type = forms.ChoiceField(label=_("Report type"), choices=report_types)


class EventSummaryReport(SimpleReport):
    title = _("Event Summary")
    form = ReportForm

    @staticmethod
    def get_by_event_class():
        """ Summary by event class """
        c = ActiveEvent.objects.item_frequencies("event_class")
        r = []
        for k, v in c.items():
            if not k:
                continue
            r += [[EventClass.objects.filter(id=k).first(), int(v)]]
        return sorted(r, key=lambda x: -x[1])

    @staticmethod
    def get_by_object():
        """Summary by managed object"""
        c = ActiveEvent.objects.item_frequencies("managed_object")
        r = []
        for k, v in c.items():
            if not k:
                continue
            r += [[ManagedObject.objects.get(id=k), int(v)]]
        return sorted(r, key=lambda x: -x[1])

    @staticmethod
    def get_by_profile():
        """Summary by managed object's profile"""
        c = ActiveEvent.objects.item_frequencies("managed_object")
        pc = {}
        mo_map = {}  # managed object id -> profile name
        for k, v in c.items():
            if not k:
                continue
            try:
                p = mo_map[k]
            except KeyError:
                p = ManagedObject.objects.get(id=k).profile.name
                mo_map[k] = p
            try:
                pc[p] += v
            except KeyError:
                pc[p] = v
        return sorted(pc.items(), key=lambda x: -x[1])

    @staticmethod
    def get_by_status():
        return [
            ("Failed", FailedEvent.objects.count()),
            ("Active", ActiveEvent.objects.count()),
            ("Archived", ArchivedEvent.objects.count())
        ]

    def get_data(self, request, report_type=None, **kwargs):
        if report_type == "class":
            # Summary by class
            columns = ["Event Class"]
            data = self.get_by_event_class()
        elif report_type == "object":
            # Summary by object
            columns = ["Managed Object"]
            data = self.get_by_object()
        elif report_type == "profile":
            # Summary by profile
            columns = ["Profile"]
            data = self.get_by_profile()
        elif report_type == "status":
            # Summary by event status
            columns = ["Status"]
            data = self.get_by_status()
        else:
            raise Exception("Invalid report type: %s" % report_type)
        title = self.title
        for r, t in report_types:
            if r == report_type:
                title += ": " + t
                break
        columns += [TableColumn("Quantity", align="right",
                                total="sum", format="integer")]
        return self.from_dataset(title=title, columns=columns,
                                 data=data, enumerate=True)
