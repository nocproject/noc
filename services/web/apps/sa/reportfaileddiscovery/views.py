# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## Failed Scripts Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

from django import forms
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn, PredefinedReport
from noc.lib.nosql import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    pool = forms.ModelChoiceField(
        label=_("Managed Objects Pools"),
        required=True,
        queryset=Pool.objects.order_by("name"))
    obj_profile = forms.ModelChoiceField(
        label=_("Managed Objects Profile"),
        required=False,
        queryset=ManagedObjectProfile.objects.order_by("name"))
    avail_status = forms.BooleanField(
        label=_("Filter by Ping status"),
        required=False
    )


class ReportFilterApplication(SimpleReport):
    title = _("Failed Discovery")
    form = ReportForm
    predefined_reports = {
        "default": PredefinedReport(
            _("Failed Discovery (default)"), {
                "pool": "default"
            }
        ),
        "MO": PredefinedReport(
            _("Failed Discovery (MO)"), {
                "pool": "MO"
            }
        ),
        "Lipets": PredefinedReport(
            _("Failed Discovery (Lipetsk)"), {
                "pool": 30 * 86400
            }
        )
    }

    def get_data(self, request, pool="default", obj_profile=None, avail_status=None, **kwargs):
        data = []
        job_logs = get_db()["noc.joblog"].find({"$and": [{"problems": {"$ne": {  }}},
                                                         {"problems": {"$exists": "true"}}]})
        for discovery in job_logs:
            mo = ManagedObject.objects.filter(id=int(discovery["_id"].split("-")[2]), pool=pool)
            if not request.user.is_superuser:
                mo = ManagedObject.objects.filter(id=int(discovery["_id"].split("-")[2]),
                                                  pool=pool,
                                                  administrative_domain__in=UserAccess.get_domains(request.user))
            if obj_profile:
                mo = mo.filter(object_profile=obj_profile)
            if not mo:
                continue
            if avail_status:
                if not mo[0].get_status():
                    continue
            for method in discovery["problems"]:

                data += [
                    (
                        mo[0].name,
                        mo[0].address,
                        mo[0].get_status(),
                        method,
                        discovery["problems"][method]
                    )
                ]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"),
                TableColumn(_("Avail"), format="bool"),
                _("Discovery"), _("Error")
            ],
            data=data)
