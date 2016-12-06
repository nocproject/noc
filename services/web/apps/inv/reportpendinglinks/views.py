# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## inv.reportdiscovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
## Python modules
import operator
from django import forms
## NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.lib.nosql import get_db
from pymongo import ReadPreference
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobject import ManagedObjectProfile
from noc.main.models.pool import Pool
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
import re


class ReportForm(forms.Form):
    pool = forms.ModelChoiceField(
        label=_("Managed Objects Pools"),
        required=True,
        queryset=Pool.objects.order_by("name"))
    obj_profile = forms.ModelChoiceField(
        label=_("Managed Objects Profile"),
        required=False,
        queryset=ManagedObjectProfile.objects.order_by("name"))


class ReportDiscoveryTopologyProblemApplication(SimpleReport):
    title = _("Pending Links")
    form = ReportForm

    def get_data(self, request, pool, obj_profile=None, **kwargs):
        rg = re.compile("Pending\slink:\s(?P<local_iface>\S+)\s-\s(?P<remote_mo>.+?):(?P<remote_iface>\S+)",
                        re.IGNORECASE)
        problems = {}  # id -> problem
        problem = {"Not found iface on remote": "->",
                   "Not found local iface on remote": "<-",
                   "Remote object is not found": "X"}
        data = []

        # Get all managed objects
        mos = ManagedObject.objects.filter(is_managed=True, pool=pool)

        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if obj_profile:
            mos = mos.filter(object_profile=obj_profile)

        mos_id = dict((mo.id, mo) for mo in mos)

        mos_job = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" % id for id in mos_id]

        n = 0
        while mos_job[(0 + n):(10000 + n)]:
            job_logs = get_db()["noc.joblog"].aggregate([{"$match": {"$and": [
                {"_id": {"$in": mos_job[(0 + n):(10000 + n)]}},
                {"problems.lldp": {"$exists": True}}]}},
                {"$project": {"_id": 1, "problems.lldp": 1}}],
                read_preference=ReadPreference.SECONDARY_PREFERRED)

            for discovery in job_logs["result"]:
                if "RPC Error:" in discovery["problems"]["lldp"] or \
                                "Unhandled exception" in discovery["problems"]["lldp"]:
                    continue
                mo_id = discovery["_id"].split("-")[2]
                print(discovery["problems"]["lldp"])
                for iface in discovery["problems"]["lldp"]:
                    print iface
                    if "is not found" in discovery["problems"]["lldp"][iface]:
                        problems[mo_id] = {iface: {
                            "problem": "Remote object is not found",
                            "remote_id": discovery["problems"]["lldp"][iface]}}
                    if "Pending link:" in discovery["problems"]["lldp"][iface]:
                        pend_str = rg.match(discovery["problems"]["lldp"][iface])
                        rmo = ManagedObject.objects.get(name=pend_str.group("remote_mo"))
                        mo = mos_id.get(mo_id, ManagedObject.get_by_id(mo_id))
                        problems[mo_id] = {iface: {
                            "problem": "Not found iface on remote",
                            "remote_id": "%s; %s ;%s" % (rmo.name, rmo.profile_name, pend_str.group("remote_iface")),
                            "remote_iface": pend_str.group("remote_iface")}}
                        problems[rmo.id] = {pend_str.group("remote_iface"): {
                            "problem": "Not found local iface on remote",
                            "remote_id": "%s; %s; %s" % (mo.name, mo.profile_name, pend_str.group("remote_iface")),
                            "remote_iface": pend_str.group("remote_iface")}}
                    # print(discovery["problems"]["lldp"])
                pass

            n += 10000
        for mo_id in problems:
            mo = mos_id.get(mo_id, ManagedObject.get_by_id(mo_id))
            for iface in problems[mo_id]:
                data += [(
                    mo.name,
                    mo.address,
                    mo.profile_name,
                    iface,
                    problem[problems[mo_id][iface]["problem"]],
                    problems[mo_id][iface]["remote_id"]
                )]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"), _("Profile"), _("Interface"),
                _("Direction"), _("Remote Object")
                # _("Discovery"), _("Error")
            ],
            data=data)
