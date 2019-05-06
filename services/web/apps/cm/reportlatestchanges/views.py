# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Latest Change Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import datetime
# Third-party modules
from django import forms
from pymongo import ReadPreference
# NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.lib.nosql import get_db
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobject import ManagedObject
from noc.dns.models.dnszone import DNSZone
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    repo = forms.ChoiceField(label=_("Type"),
                             choices=[("config", "config"),
                                      ("dnszone", "DNS")])
    days = forms.IntegerField(label=_("In Days"), min_value=1)


class ReportLatestChangesApplication(SimpleReport):
    title = _("Latest Changes")
    form = ReportForm

    def get_data(self, request, repo="config", days=1, **kwargs):
        baseline = datetime.datetime.now() - datetime.timedelta(days=days)
        coll = get_db()["noc.gridvcs.%s.files" % repo].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED)
        pipeline = [
            {"$match": {"ts": {"$gte": baseline}}},
            {"$group": {"_id": "$object", "last_ts": {"$max": "$ts"}}},
            {"$sort": {"_id": 1}}
        ]
        if repo == "config" and not request.user.is_superuser:
            objects = ManagedObject.objects.filter(
                administrative_domain__in=UserAccess.get_domains(request.user)).values_list("id", "name")
            pipeline = [{"$match": {"object": {"$in": objects}}}] + pipeline
        # Perform query
        data = list(coll.aggregate(pipeline))
        # Resolve names
        if data:
            seen_ids = list(set(d["_id"] for d in data))
            n_map = {}
            if repo == "config":
                n_map = dict(ManagedObject.objects.filter(id__in=list(seen_ids)).values_list("id", "name"))
            elif repo == "dns":
                n_map = dict(DNSZone.objects.filter(id__in=list(seen_ids)).values_list("id", "name"))
            result = [(d["_id"], n_map.get(d["_id"], "-"), d["last_ts"]) for d in data]
        else:
            result = []
        return self.from_dataset(
            title="%s: %s in %d days" % (self.title, repo, days),
            columns=[
                "ID",
                "Name",
                TableColumn(_("Last Changed"), format="datetime")],
            data=result,
            enumerate=True
        )
