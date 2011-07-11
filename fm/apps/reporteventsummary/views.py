# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event Summary Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.fm.models import ActiveEvent, EventClass, ManagedObject,\
                          NewEvent, FailedEvent, ArchivedEvent

## Report types
report_types = [
            ("class", "By Event Class"),
            ("object", "By Managed Object"),
            ("profile", "By Profile"),
            ("status", "By Status")
            ]


class ReportForm(forms.Form):
    report_type = forms.ChoiceField(choices=report_types)


class EventSummaryReport(SimpleReport):
    title = "Event Summary"
    form = ReportForm

    def get_by_event_class(self):
        """ Summary by event class """
        c = ActiveEvent.objects.item_frequencies("event_class")
        r = []
        for k, v in c.items():
            r += [[EventClass.objects.filter(id=k).first(), int(v)]]
        return sorted(r, key=lambda x: -x[1])

    def get_by_object(self):
        """Summary by managed object"""
        c = ActiveEvent.objects.item_frequencies("managed_object")
        r = []
        for k, v in c.items():
            r += [[ManagedObject.objects.get(id=k), int(v)]]
        return sorted(r, key=lambda x: -x[1])

    def get_by_profile(self):
        """Summary by managed object's profile"""
        c = ActiveEvent.objects.item_frequencies("managed_object")
        pc = {}
        mo_map = {}  # managed object id -> profile name
        for k, v in c.items():
            try:
                p = mo_map[k]
            except KeyError:
                p = ManagedObject.objects.get(id=k).profile_name
                mo_map[k] = p
            try:
                pc[p] += v
            except KeyError:
                pc[p] = v
        return sorted(pc.items(), key=lambda x: -x[1])

    def get_by_status(self):
        return [
            ("New", NewEvent.objects.count()),
            ("Failed", FailedEvent.objects.count()),
            ("Active", ActiveEvent.objects.count()),
            ("Archived", ArchivedEvent.objects.count())
        ]

    def get_data(self, report_type, **kwargs):
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
        for r, t in report_types:
            if r == report_type:
                title = self.title + ": " + t
                break
        columns += [TableColumn("Quantity", align="right",
                                total="sum", format="integer")]
        return self.from_dataset(title=title, columns=columns,
                                 data=data, enumerate=True)
