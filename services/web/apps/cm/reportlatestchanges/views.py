# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Latest Change Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
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
from noc.cm.models import Object
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    """
    Report Form
    """
    repo = forms.ChoiceField(label=_("Type"),
                             choices=[("config", "config"),
                                      ("prefix-list", "prefix-list")])
    days = forms.IntegerField(label=_("In Days"), min_value=1)


class ReportreportLatestChanges(SimpleReport):
    title = _("Latest Changes")
    form = ReportForm

    def get_data(self, request, repo="config", days=1, **kwargs):
        data = []
        baseline = datetime.datetime.now() - datetime.timedelta(days=days)
        if repo == "config":
            mos = ManagedObject.objects.filter()
            if not request.user.is_superuser:
                mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
            mos = dict(mos.values_list("id", "name"))
            config_db = get_db()["noc.gridvcs.config.files"].with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED)
            pipeline = [{"$match": {"ts": {"$gte": baseline}}},
                        {"$group": {"_id": "$object", "last_ts": {"$max": "$ts"}}},
                        {"$sort": {"_id": 1}}]
            for value in config_db.aggregate(pipeline):
                if value["_id"] not in mos:
                    continue
                data += [(mos[value["_id"]], value["last_ts"])]

        else:
            oc = Object.get_object_class(repo)
            data = [(o, o.last_modified) for o in
                    oc.objects.filter(last_modified__gte=baseline).order_by("-last_modified")]
        return self.from_dataset(
            title="%s: %s in %d days" % (self.title, repo, days),
            columns=[
                "Object",
                TableColumn(_("Last Changed"), format="datetime")],
            data=data,
            enumerate=True)
