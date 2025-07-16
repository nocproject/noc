# ----------------------------------------------------------------------
# pendinglinksds datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
import ast
from collections import defaultdict
import re
from typing import Any, Optional, Iterable, List, Tuple, AsyncIterable

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from .base import BaseDataSource, FieldInfo, ParamInfo
from noc.core.mongo.connection import get_db
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.link import Link
from noc.inv.models.discoveryid import DiscoveryID
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile


def pending_links(ids, ignore_profiles=None, filter_exists_link=False):
    result = defaultdict(dict)  # id -> problem
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
                    result[mo.id] = {
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
                    result[mo.id][iface] = {
                        "problem": "Not found iface on remote",
                        "detail": detail,
                        "remote_id": "%s::: %s" % (rmo.name, rmo.profile.name),
                        "remote_iface": pend_str.group("remote_iface"),
                    }
                    result[rmo.id][pend_str.group("remote_iface")] = {
                        "problem": "Not found local iface on remote",
                        "detail": detail,
                        "remote_id": "%s::: %s" % (mo.name, mo.profile.name),
                        "remote_iface": iface,
                    }
        n += 10000
    return result


class PendingLinksDS(BaseDataSource):
    name = "pendinglinksds"

    fields = [
        FieldInfo(name="managed_object"),
        FieldInfo(name="address"),
        FieldInfo(name="profile"),
        FieldInfo(name="administrative_domain"),
        FieldInfo(name="interface"),
        FieldInfo(name="direction"),
        FieldInfo(name="remote_interface"),
        FieldInfo(name="remote_object"),
        FieldInfo(name="detail"),
        FieldInfo(name="remote_hostname"),
        FieldInfo(name="remote_description"),
        FieldInfo(name="remote_chassis"),
    ]

    params = [
        ParamInfo(name="pool", type="str", model="main.Pool", required=True),
        ParamInfo(name="mo_profile", type="str", model="sa.ManagedObjectProfile"),
        ParamInfo(name="show_already_linked", type="bool", default=False),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        pool: Optional[Pool] = None,
        mo_profile: Optional[ManagedObjectProfile] = None,
        show_already_linked=False,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Any]]:
        print("kwargs", kwargs, type(kwargs))
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
        mos = ManagedObject.objects.filter(is_managed=True, pool=pool).values("id")
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        if mo_profile:
            mos = mos.filter(object_profile=mo_profile)
        mos_id = {mo["id"]: mo for mo in mos}
        problems = pending_links(
            list(mos_id),
            ignore_profiles=list(InterfaceProfile.objects.filter(discovery_policy="I")),
            filter_exists_link=not show_already_linked,
        )
        for mo_id in problems:
            mo = ManagedObject.get_by_id(mo_id)
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
        # data += [SectionRow(name="Summary information on u_object")]
        # for c in not_found:
        #    if not_found[c] > 4:
        #        data += [c]
        # data += [SectionRow(name="Summary information on agg")]
        # for c in local_on_remote:
        #    if local_on_remote[c] > 4:
        #        data += [c]
        row_num = 0
        for o in data:
            row_num += 1
            yield row_num, "managed_object", o[0]
            yield row_num, "address", o[1]
            yield row_num, "profile", o[2]
            yield row_num, "administrative_domain", o[3]
            yield row_num, "interface", o[4]
            yield row_num, "direction", o[5]
            yield row_num, "remote_interface", o[6]
            yield row_num, "remote_object", o[7]
            yield row_num, "detail", o[8]
            yield row_num, "remote_hostname", o[9]
            yield row_num, "remote_description", o[10]
            yield row_num, "remote_chassis", o[11]
