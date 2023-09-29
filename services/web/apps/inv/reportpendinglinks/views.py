# ---------------------------------------------------------------------
# inv.reportdiscovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
import ast

# Third-party modules
from django import forms

# NOC modules
from noc.core.cache.base import cache
from noc.services.web.base.simplereport import SimpleReport, SectionRow
from noc.core.mongo.connection import get_db
from pymongo import ReadPreference
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobject import ManagedObjectProfile
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.link import Link
from noc.inv.models.discoveryid import DiscoveryID
from noc.main.models.pool import Pool
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportPendingLinks(object):
    def __init__(self, ids, cache_key=None, ignore_profiles=None, filter_exists_link=False):
        self.ids = ids
        self.ignore_profiles = ignore_profiles
        self.filter_exists_link = filter_exists_link
        if cache_key:
            self.out = cache.get(key=cache_key)
            if not self.out:
                self.out = self.load(self.ids, self.ignore_profiles, self.filter_exists_link)
                cache.set(cache_key, self.out, ttl=28800)
        else:
            self.out = self.load(self.ids, self.ignore_profiles, self.filter_exists_link)

    @staticmethod
    def load(ids, ignore_profiles=None, filter_exists_link=False):
        problems = defaultdict(dict)  # id -> problem
        rx_nf = re.compile(r"Remote object '(.*?)' is not found")
        rg = re.compile(
            r"Pending\slink:\s(?P<local_iface>.+?)(\s-\s)(?P<remote_mo>.+?):(?P<remote_iface>\S+)",
            re.IGNORECASE,
        )
        mos_job = [
            "discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" % mo_id
            for mo_id in ids
        ]
        n = 0
        ignored_ifaces = []
        find = DiscoveryID._get_collection().aggregate(
            [
                {"$unwind": "$macs"},
                {"$group": {"_id": "$macs", "count": {"$sum": 1}, "mo": {"$push": "$object"}}},
                {"$match": {"count": {"$gt": 1}}},
                {"$unwind": "$mo"},
                {"$group": {"_id": "", "mos": {"$addToSet": "$mo"}}},
            ],
            allowDiskUse=True,
        )
        duplicate_macs = set()
        find = next(find, None)
        if find:
            duplicate_macs = set(find["mos"])
        while mos_job[(0 + n) : (10000 + n)]:
            job_logs = (
                get_db()["noc.joblog"]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(
                    [
                        {
                            "$match": {
                                "$and": [
                                    {"_id": {"$in": mos_job[(0 + n) : (10000 + n)]}},
                                    {"problems.lldp": {"$exists": True}},
                                ]
                            }
                        },
                        {"$project": {"_id": 1, "problems.lldp": 1}},
                    ]
                )
            )

            for discovery in job_logs:
                if (
                    "RPC Error:" in discovery["problems"]["lldp"]
                    or "Unhandled exception" in discovery["problems"]["lldp"]
                ):
                    continue
                mo_id = discovery["_id"].split("-")[2]
                mo = ManagedObject.get_by_id(mo_id)
                # log.debug("%s", discovery["problems"]["lldp"])
                # print(discovery["problems"]["lldp"])
                if ignore_profiles:
                    ignored_ifaces += [
                        (mo_id, iface.name)
                        for iface in Interface.objects.filter(
                            managed_object=mo,
                            # name__in=discovery["problems"]["lldp"].keys(),
                            profile__in=ignore_profiles,
                        )
                    ]
                for iface in discovery["problems"]["lldp"]:
                    if (mo.id, iface) in ignored_ifaces:
                        continue
                    # print iface
                    match = rx_nf.search(discovery["problems"]["lldp"][iface])
                    if match:
                        parsed_x = ast.literal_eval(match.group(1))
                        problems[mo.id] = {
                            iface: {
                                "problem": "Remote object is not found",
                                "detail": "Remote object not in system or ID discovery not success",
                                "remote_id": "",
                                "remote_iface": parsed_x.get("remote_port"),
                                "remote_hostname": parsed_x.get("remote_system_name"),
                                "remote_description": parsed_x.get("remote_system_description"),
                                "remote_chassis": parsed_x.get("remote_chassis_id"),
                            }
                        }
                    if "Pending link:" in discovery["problems"]["lldp"][iface]:
                        pend_str = rg.search(discovery["problems"]["lldp"][iface])
                        try:
                            rmo = ManagedObject.objects.get(name=pend_str.group("remote_mo"))
                        except ManagedObject.DoesNotExist:
                            continue
                        if (
                            filter_exists_link
                            and Link.objects.filter(linked_objects=[mo.id, rmo.id]).first()
                        ):
                            # If already linked on other proto
                            continue
                        detail = ""
                        if mo.id in duplicate_macs or rmo.id in duplicate_macs:
                            detail = "Duplicate ID"
                        # mo = mos_id.get(mo_id, ManagedObject.get_by_id(mo_id))
                        problems[mo.id][iface] = {
                            "problem": "Not found iface on remote",
                            "detail": detail,
                            "remote_id": "%s::: %s" % (rmo.name, rmo.profile.name),
                            "remote_iface": pend_str.group("remote_iface"),
                        }
                        problems[rmo.id][pend_str.group("remote_iface")] = {
                            "problem": "Not found local iface on remote",
                            "detail": detail,
                            "remote_id": "%s::: %s" % (mo.name, mo.profile.name),
                            "remote_iface": iface,
                        }
                        # print(discovery["problems"]["lldp"])
            n += 10000
        return problems


class ReportDiscoveryTopologyProblemApplication(SimpleReport):
    title = _("Pending Links")

    def get_form(self):
        class ReportForm(forms.Form):
            pool = forms.ChoiceField(
                label=_("Managed Objects Pools"),
                required=True,
                choices=list(Pool.objects.order_by("name").scalar("id", "name"))
                + [(None, "-" * 9)],
            )
            obj_profile = forms.ModelChoiceField(
                label=_("Managed Objects Profile"),
                required=False,
                queryset=ManagedObjectProfile.objects.order_by("name"),
            )
            show_already_linked = forms.BooleanField(
                label=_("Show problem on already linked"), required=False
            )

        return ReportForm

    def get_data(
        self,
        request,
        pool=None,
        obj_profile=None,
        show_already_linked=False,
        filter_ignore_iface=True,
        **kwargs,
    ):

        rn = re.compile(
            r"'remote_chassis_id': u'(?P<rem_ch_id>\S+)'.+'remote_system_name': u'(?P<rem_s_name>\S+)'",
            re.IGNORECASE,
        )
        problem = {
            "Not found iface on remote": "->",
            "Not found local iface on remote": "<-",
            "Remote object is not found": "X",
        }
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
        mos_id = {mo.id: mo for mo in mos}
        report = ReportPendingLinks(
            list(mos_id),
            ignore_profiles=list(InterfaceProfile.objects.filter(discovery_policy="I")),
            filter_exists_link=not show_already_linked,
        )
        problems = report.out
        for mo_id in problems:
            mo = mos_id.get(mo_id, ManagedObject.get_by_id(mo_id))
            for iface in problems[mo_id]:
                data += [
                    (
                        mo.name,
                        mo.address,
                        mo.profile.name,
                        mo.administrative_domain.name,
                        iface,
                        problem[problems[mo_id][iface]["problem"]],
                        problems[mo_id][iface]["remote_iface"],
                        problems[mo_id][iface]["remote_id"],
                        problems[mo_id][iface]["detail"],
                        problems[mo_id][iface].get("remote_hostname"),
                        problems[mo_id][iface].get("remote_description"),
                        problems[mo_id][iface].get("remote_chassis"),
                    )
                ]
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
                _("Managed Object"),
                _("Address"),
                _("Profile"),
                _("Administrative domain"),
                _("Interface"),
                _("Direction"),
                _("Remote Interface"),
                _("Remote Object"),
                _("Detail"),
                _("Remote Hostname"),
                _("Remote Description"),
                _("Remote Chassis"),
                # _("Discovery"), _("Error")
            ],
            data=data,
        )
