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
        label=_("Managed Objects Pool"),
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
    profile_check_only = forms.BooleanField(
        label=_("Profile check only"),
        required=False
    )
    failed_scripts_only = forms.BooleanField(
        label=_("Failed discovery only"),
        required=False
    )


class ReportFilterApplication(SimpleReport):
    title = _("Failed Discovery")
    form = ReportForm
    predefined_reports = {
        "default": PredefinedReport(
            _("Failed Discovery (default)"), {
                "pool": Pool.objects.get(name="default")
            }
        )
    }

    def get_data(self, request, pool="default", obj_profile=None,
                 avail_status=None, profile_check_only=None, failed_scripts_only=None, **kwargs):
        data = []
        if profile_check_only:
            job_logs = get_db()["noc.joblog"].find({"$or": [{"problems.suggest_cli": {"$exists": True}},
                                                            {"problems.suggest_snmp": {"$exists": True}}]},
                                                   {"_id": 1, "problems.suggest_snmp": 1, "problems.suggest_cli": 1})
        elif failed_scripts_only:
            job_logs = get_db()["noc.joblog"].find({"$and": [{"problems": {"$exists": "true", "$ne": {  }}},
                                                             {"problems.suggest_snmp": {"$exists": False}},
                                                             {"problems.suggest_cli": {"$exists": False}}]})
        else:
            job_logs = get_db()["noc.joblog"].find({"problems": {"$exists": True, "$ne": {  }}})

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
