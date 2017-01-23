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
from noc.lib.app.simplereport import SimpleReport, TableColumn, PredefinedReport, SectionRow
from noc.lib.nosql import get_db
from pymongo import ReadPreference
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.objectstatus import ObjectStatus
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
    filter_pending_links = forms.BooleanField(
        label=_("Filter Pending links"),
        required=False
    )
    filter_none_objects = forms.BooleanField(
        label=_("Filter None problems"),
        required=False
    )


class ReportFilterApplication(SimpleReport):
    title = _("Discovery Problem")
    form = ReportForm
    predefined_reports = {
        "default": PredefinedReport(
            _("Failed Discovery 2(default)"), {
                "pool": Pool.objects.get(name="default")
            }
        )
    }

    def get_data(self, request, pool=Pool.get_by_name("default"), obj_profile=None,
                 avail_status=None, profile_check_only=None,
                 failed_scripts_only=None, filter_pending_links=None,
                 filter_none_objects=None,
                 **kwargs):
        data = []
        avail = {}

        data += [SectionRow(name="Report by %s" % pool.name)]
        mos = ManagedObject.objects.filter(pool=pool, is_managed=True)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if obj_profile:
            mos = mos.filter(object_profile=obj_profile)
        discovery = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
        mos_id = list(mos.values_list("id", flat=True))
        if avail_status:
            avail = ObjectStatus.get_statuses(mos_id)

        if profile_check_only:
            match = {"$or": [{"job.problems.suggest_cli": {"$exists": True}},
                             {"job.problems.suggest_snmp": {"$exists": True}}]}

        elif failed_scripts_only:
            match = {"$and": [
                {"job.problems": {"$exists": "true", "$ne": {}}},
                {"job.problems.suggest_snmp": {"$exists": False}},
                {"job.problems.suggest_cli": {"$exists": False}}]}
        else:
            match = {"job.problems": {"$exists": True, "$ne": {  }}}

        pipeline = [
            {"$match": {"key": {"$in": mos_id}, "jcls": discovery}},
            {"$project": {
                "j_id": {"$concat": ["discovery-", "$jcls", "-", {"$substr": ["$key", 0, -1]}]},
                "st": True,
                "key": True}},
            {"$lookup": {"from": "noc.joblog", "localField": "j_id", "foreignField": "_id", "as": "job"}},
            {"$project": {"job.problems": True, "st": True, "key": True}},
            {"$match": match}]

        r = get_db()["noc.schedules.discovery.%s" % pool.name].aggregate(pipeline,
                                                                            read_preference=ReadPreference.SECONDARY_PREFERRED)

        for discovery in r["result"]:

                # mo = ManagedObject.get_by_id(int(discovery["_id"].split("-")[2]))
                mo = ManagedObject.get_by_id(discovery["key"])
                if avail_status:
                    if not avail.get(discovery["key"], None):
                        continue
                for method in discovery["job"][0]["problems"]:
                    if filter_pending_links:
                        if method == "lldp":
                            if not ("RPC Error" in discovery["job"][0]["problems"][method]
                                    or "exception" in discovery["job"][0]["problems"][method]):
                                continue
                    if filter_none_objects:
                        if "RPC Error: Failed: None" in discovery["job"][0]["problems"][method]:
                            continue

                    data += [
                        (
                            mo.name,
                            mo.address,
                            mo.profile_name,
                            _("Yes") if mo.get_status() else _("No"),
                            discovery["st"].strftime("%d.%m.%Y"),
                            method,
                            discovery["job"][0]["problems"][method].replace("\n", " ").replace("\r", " ") if
                            isinstance(discovery["job"][0]["problems"][method], str) else
                            discovery["job"][0]["problems"][method]
                        )
                    ]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"), _("Profile"),
                _("Avail"), _("Last successful discovery"),
                _("Discovery"), _("Error")
            ],
            data=data)
