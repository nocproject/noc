# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# inv.reportdiscovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
# Python modules
import operator
import re
from collections import defaultdict
from django import forms
# NOC modules
from noc.core.cache.base import cache
from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.lib.nosql import get_db
from pymongo import ReadPreference
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobject import ManagedObjectProfile
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.main.models.pool import Pool
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


class ReportPendingLinks(object):
    def __init__(self, ids, cache_key=None, ignore_profiles=None):
        self.ids = ids
        self.ignore_profiles = ignore_profiles
        if cache_key:
            self.out = cache.get(key=cache_key)
            if not self.out:
                self.out = self.load(self.ids, self.ignore_profiles)
                cache.set(cache_key, self.out, ttl=28800)
        else:
            self.out = self.load(self.ids, self.ignore_profiles)

    @staticmethod
    def load(ids, ignore_profiles=None):
        problems = defaultdict(dict)  # id -> problem
        rg = re.compile("Pending\slink:\s(?P<local_iface>.+?)(\s-\s)(?P<remote_mo>.+?):(?P<remote_iface>\S+)",
                        re.IGNORECASE)

        mos_job = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" % mo_id for mo_id in ids]
        n = 0
        ignored_ifaces = []
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
                mo = ManagedObject.get_by_id(mo_id)
                # log.debug("%s", discovery["problems"]["lldp"])
                # print(discovery["problems"]["lldp"])
                if ignore_profiles:
                    ignored_ifaces += [(mo_id, iface.name) for iface in
                                       Interface.objects.filter(managed_object=mo,
                                                                # name__in=discovery["problems"]["lldp"].keys(),
                                                                profile__in=ignore_profiles)]
                for iface in discovery["problems"]["lldp"]:
                    if (mo_id, iface) in ignored_ifaces:
                        continue
                    # print iface
                    if "is not found" in discovery["problems"]["lldp"][iface]:
                        problems[mo_id] = {iface: {
                            "problem": "Remote object is not found",
                            "remote_id": discovery["problems"]["lldp"][iface]}}
                    if "Pending link:" in discovery["problems"]["lldp"][iface]:
                        pend_str = rg.match(discovery["problems"]["lldp"][iface])
                        try:
                            rmo = ManagedObject.objects.get(name=pend_str.group("remote_mo"))
                        except ManagedObject.DoesNotExist:
                            continue
                        # mo = mos_id.get(mo_id, ManagedObject.get_by_id(mo_id))
                        problems[mo_id][iface] = {
                            "problem": "Not found iface on remote",
                            "remote_id": "%s; %s ;%s" % (rmo.name, rmo.profile.name, pend_str.group("remote_iface")),
                            "remote_iface": pend_str.group("remote_iface")}
                        problems[rmo.id][pend_str.group("remote_iface")] = {
                            "problem": "Not found local iface on remote",
                            "remote_id": "%s; %s; %s" % (mo.name, mo.profile.name, iface),
                            "remote_iface": pend_str.group("remote_iface")}
                        # print(discovery["problems"]["lldp"])
                pass

            n += 10000

        return problems


class ReportDiscoveryTopologyProblemApplication(SimpleReport):
    title = _("Pending Links")
    form = ReportForm

    def get_data(self, request, pool, obj_profile=None, filter_ignore_iface=True, **kwargs):

        rn = re.compile("'remote_chassis_id': u'(?P<rem_ch_id>\S+)'.+'remote_system_name': u'(?P<rem_s_name>\S+)'",
                        re.IGNORECASE)
        problem = {"Not found iface on remote": "->",
                   "Not found local iface on remote": "<-",
                   "Remote object is not found": "X"}
        data = []
        # MAC, hostname, count
        not_found = defaultdict(int)
        # Name, IP, count
        local_on_remote = defaultdict(int)
        # Get all managed objects
        mos = ManagedObject.objects.filter(is_managed=True, pool=pool)

        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if obj_profile:
            mos = mos.filter(object_profile=obj_profile)

        mos_id = dict((mo.id, mo) for mo in mos)
        report = ReportPendingLinks(mos_id.keys(),
                                    ignore_profiles=list(InterfaceProfile.objects.filter(discovery_policy="I")))

        problems = report.out
        for mo_id in problems:
            mo = mos_id.get(mo_id, ManagedObject.get_by_id(mo_id))
            for iface in problems[mo_id]:
                data += [(
                    mo.name,
                    mo.address,
                    mo.profile.name,
                    mo.administrative_domain.name,
                    iface,
                    problem[problems[mo_id][iface]["problem"]],
                    problems[mo_id][iface]["remote_id"]
                )]
                if problems[mo_id][iface]["problem"] == "Remote object is not found":
                    match = rn.findall(problems[mo_id][iface]["remote_id"])
                    if match:
                        not_found[match[0]] += 1
                elif problems[mo_id][iface]["problem"] == "Not found iface on remote":
                    local_on_remote[(mo.name, mo.address)] += 1

        data += [SectionRow(name="Summary information on u_object")]
        for c in not_found:
            if not_found[c] > 4:
                data += [c]
        data += [SectionRow(name="Summary information on agg")]
        for c in local_on_remote:
            if local_on_remote[c] > 4:
                data += [c]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"), _("Profile"), _("Administrative domain"),
                _("Interface"), _("Direction"), _("Remote Object")
                # _("Discovery"), _("Error")
            ],
            data=data)
