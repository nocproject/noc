# ---------------------------------------------------------------------
# Event Summary Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
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
    ("status", _("By Status")),
]


class ReportForm(forms.Form):
    report_type = forms.ChoiceField(label=_("Report type"), choices=report_types)


class EventSummaryReport(SimpleReport):
    title = _("Event Summary")
    form = ReportForm

    @staticmethod
    def get_data_db(name):
        data = list(ActiveEvent._get_collection().aggregate(
            [{
                "$group": {
                    "_id": f"${name}",
                    "count": {"$sum": 1},
                },
            },
                {
                    "$sort": {"count": -1, "_id": 1}
                }
            ],
            allowDiskUse=True,
        )
        )
        return data

    @staticmethod
    def get_by_event_class(self):
        """Summary by event class"""
        data = self.get_data_db("event_class")
        return ([EventClass.objects.filter(id=x["_id"]).first(), int(x["count"])] for x in data)

    @staticmethod
    def get_by_object(self):
        """Summary by managed object"""
        data = self.get_data_db("managed_object")
        return ([ManagedObject.objects.get(id=x["_id"]), int(x["count"])] for x in data)

    @staticmethod
    def get_by_profile(self):
        """Summary by managed object's profile"""
        data = self.get_data_db("managed_object")
        pc = {}
        mo_map = {}  # managed object id -> profile name
        for x in data:
            if not x:
                continue
            try:
                p = mo_map[x["_id"]]
            except KeyError:
                p = ManagedObject.objects.get(id=x["_id"]).profile.name
                mo_map[x["_id"]] = p
            try:
                pc[p] += x["count"]
            except KeyError:
                pc[p] = x["count"]
        return sorted(pc.items(), key=lambda x: -x[1])

    @staticmethod
    def get_by_status():
        return [
            ("Failed", FailedEvent.objects.count()),
            ("Active", ActiveEvent.objects.count()),
            ("Archived", ArchivedEvent.objects.count()),
        ]

    def get_data(self, request, report_type=None, **kwargs):
        if report_type == "class":
            # Summary by class
            columns = ["Event Class"]
            data = self.get_by_event_class(self)
        elif report_type == "object":
            # Summary by object
            columns = ["Managed Object"]
            data = self.get_by_object(self)
        elif report_type == "profile":
            # Summary by profile
            columns = ["Profile"]
            data = self.get_by_profile(self)
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
        columns += [TableColumn("Quantity", align="right", total="sum", format="integer")]
        return self.from_dataset(title=title, columns=columns, data=data, enumerate=True)
