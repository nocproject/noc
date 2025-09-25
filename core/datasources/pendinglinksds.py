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

DISCOVERY_JOB_PREFIX = "discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-"
JOBS_LIMIT = 10000

rx_not_found = re.compile(r"Remote object '(.*?)' is not found")
rx_pending_link = re.compile(
    r"Pending\slink:\s(?P<local_iface>.+?)(\s-\s)(?P<remote_mo>.+?):(?P<remote_iface>\S+)",
    re.IGNORECASE,
)
rx_nr = re.compile("[\n\r;]|&nbsp|<br/>")


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

    @staticmethod
    def pending_links(mo_ids, ignore_profiles=None, filter_exists_link=False):
        result = defaultdict(dict)  # mo_id -> {iface_name: problem}
        mo_jobs = [f"{DISCOVERY_JOB_PREFIX}{mo_id}" for mo_id in mo_ids]
        # Find list of managed objects that having some MAC-address equal to some MAC-address
        # belonging to any other managed object
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
        # Cycle through all managed object jobs by chunks
        n = 0
        while mo_jobs[(0 + n) : (JOBS_LIMIT + n)]:
            # Get one chunk
            job_logs = (
                get_db()["noc.joblog"]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(
                    [
                        {
                            "$match": {
                                "$and": [
                                    {"_id": {"$in": mo_jobs[(0 + n) : (JOBS_LIMIT + n)]}},
                                    {"problems.lldp": {"$exists": True}},
                                ]
                            }
                        },
                        {"$project": {"_id": 1, "problems.lldp": 1}},
                    ]
                )
            )
            # Cycle through jobs in the chunk
            for discovery in job_logs:
                problems_lldp = discovery["problems"]["lldp"]
                if "RPC Error:" in problems_lldp or "Unhandled exception" in problems_lldp:
                    continue
                mo_id = discovery["_id"].split("-")[2]
                mo = ManagedObject.get_by_id(mo_id)
                # Get ignored interfaces
                ignored_ifaces = []
                if ignore_profiles:
                    ignored_ifaces = [
                        (mo_id, iface.name)
                        for iface in Interface.objects.filter(
                            managed_object=mo,
                            profile__in=ignore_profiles,
                        )
                    ]
                # Cycle through problem interfaces in managed object
                for iface, iface_problem in problems_lldp.items():
                    if (mo.id, iface) in ignored_ifaces:
                        continue
                    match = rx_not_found.search(iface_problem)
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
                    if "Pending link:" in iface_problem:
                        pend_str = rx_pending_link.search(iface_problem)
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
            n += JOBS_LIMIT
        return result

    @staticmethod
    def clean_description(value: Optional[str]):
        """Replace LF, CR and some other symbols in System Description to space
        for proper data in .csv and .xlsx formats"""
        if value:
            value = rx_nr.sub(" ", value)
        return value

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
        direction_map = {
            "Not found iface on remote": "->",
            "Not found local iface on remote": "<-",
            "Remote object is not found": "X",
        }
        # Get all managed objects
        mos = ManagedObject.objects.filter(is_managed=True, pool=pool).values("id")
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        if mo_profile:
            mos = mos.filter(object_profile=mo_profile)
        mos_id = {mo["id"]: mo for mo in mos}
        problems = cls.pending_links(
            list(mos_id),
            ignore_profiles=list(InterfaceProfile.objects.filter(discovery_policy="I")),
            filter_exists_link=not show_already_linked,
        )
        row_num = 0
        for mo_id in problems:
            mo = ManagedObject.get_by_id(mo_id)
            for iface in problems[mo_id]:
                row_num += 1
                yield row_num, "managed_object", mo.name
                yield row_num, "address", mo.address
                yield row_num, "profile", mo.profile.name
                yield row_num, "administrative_domain", mo.administrative_domain.name
                yield row_num, "interface", iface
                yield row_num, "direction", direction_map[problems[mo_id][iface]["problem"]]
                yield row_num, "remote_interface", problems[mo_id][iface]["remote_iface"]
                yield row_num, "remote_object", problems[mo_id][iface]["remote_id"]
                yield row_num, "detail", problems[mo_id][iface]["detail"]
                yield row_num, "remote_hostname", problems[mo_id][iface].get("remote_hostname")
                yield (
                    row_num,
                    "remote_description",
                    cls.clean_description(problems[mo_id][iface].get("remote_description")),
                )
                yield row_num, "remote_chassis", problems[mo_id][iface].get("remote_chassis")
