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

        mos = ManagedObject.objects.filter(pool=pool)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if obj_profile:
            mos = mos.filter(object_profile=obj_profile)

        mos = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" % mo.id for mo in mos]

        n = 0
        while mos[(0 + n):(10000 + n)]:
            if profile_check_only:
                job_logs = get_db()["noc.joblog"].aggregate([{"$match":{"_id": {"$in": mos[(0 + n):(10000 + n)]}}},
                                                             {"$match": {"$or": [{"problems.suggest_cli": {"$exists": True}},
                                                                                 {"problems.suggest_snmp": {"$exists": True}}]
                                                                         }},
                                                             {"$project":{"_id": 1,
                                                                          "problems.suggest_snmp": 1,
                                                                          "problems.suggest_cli": 1}}
                                                             ])

            elif failed_scripts_only:
                job_logs = get_db()["noc.joblog"].aggregate([{"$match":{"_id": {"$in": mos[(0 + n):(10000 + n)]}}},
                                                             {"$match":{"$and": [{"problems": {"$exists": "true", "$ne": {  }}},
                                                             {"problems.suggest_snmp": {"$exists": False}},
                                                             {"problems.suggest_cli": {"$exists": False}}]}}])
            else:
                job_logs = get_db()["noc.joblog"].aggregate([{"$match": {"problems": {"$exists": True, "$ne": {  }},
                                                             "_id": {"$in": mos[(0 + n):(10000 + n)]}}}])

            for discovery in job_logs["result"]:

                mo = ManagedObject.get_by_id(int(discovery["_id"].split("-")[2]))
                if avail_status:
                    if not mo.get_status():
                        continue
                for method in discovery["problems"]:

                    data += [
                        (
                            mo.name,
                            mo.address,
                            mo.profile_name,
                            mo.get_status(),
                            method,
                            discovery["problems"][method]
                        )
                    ]
            n += 10000

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"), _("Profile"),
                TableColumn(_("Avail"), format="bool"),
                _("Discovery"), _("Error")
            ],
            data=data)
