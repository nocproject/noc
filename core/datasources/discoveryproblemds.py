# ----------------------------------------------------------------------
# Discovery Problem Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, List, Union, AsyncIterable

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from .base import FieldInfo, FieldType, ParamInfo, BaseDataSource
from noc.core.scheduler.scheduler import Scheduler
from noc.main.models.pool import Pool
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.sa.models.profile import GENERIC_PROFILE
from noc.sa.models.managedobjectprofile import ManagedObjectProfile

CODE_MAP = {
    "1": "Unknown error",
    "10000": "Unspecified CLI error",
    "10005": "Connection refused",
    "10001": "Authentication failed",
    "10002": "No super command defined",
    "10003": "No super privileges",
    "10004": "SSH Protocol error",
}


class DiscoveryProblemDS(BaseDataSource):
    name = "discoveryproblemds"
    row_index = "managed_object_id"

    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="last_success_discovery"),
        FieldInfo(name="discovery"),
        FieldInfo(name="error"),
    ]

    params = [
        ParamInfo(name="pool", type="str", model="main.Pool"),
        ParamInfo(name="resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="mo_profile", type="int", model="sa.ManagedObjectProfile"),
        ParamInfo(name="filter_no_ping", type="bool", default=False),
        ParamInfo(name="profile_check_only", type="bool", default=False),
        ParamInfo(name="failed_discovery_only", type="bool", default=False),
        ParamInfo(name="filter_pending_links", type="bool", default=False),
        ParamInfo(name="filter_none_problems", type="bool", default=False),
        ParamInfo(name="filter_view_other", type="bool", default=False),
    ]

    @classmethod
    def get_pipeline(cls, ids: List[int], match=None):
        discovery = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
        pipeline = [
            {"$match": {"key": {"$in": ids}, "jcls": discovery}},
            {
                "$project": {
                    "j_id": {"$concat": ["discovery-", "$jcls", "-", {"$substr": ["$key", 0, -1]}]},
                    "st": True,
                    "key": True,
                }
            },
            {
                "$lookup": {
                    "from": "noc.joblog",
                    "localField": "j_id",
                    "foreignField": "_id",
                    "as": "job",
                }
            },
            {"$project": {"job.problems": True, "st": True, "key": True}},
        ]
        if match:
            pipeline += [{"$match": match}]
        else:
            pipeline += [{"$match": {"job.problems": {"$exists": True, "$ne": {}}}}]
        return pipeline

    @staticmethod
    def clean_problem(problems) -> str:
        """Cleanup method problem"""
        if isinstance(problems, dict) and "" in problems:
            problem = problems.get("", "")
        if "Remote error code" in problems:
            problem = CODE_MAP.get(problems.split(" ")[-1], problems)
        if isinstance(problems, str):
            problem = problems.replace("\n", " ").replace("\r", " ")
        return problem

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        pool: Optional[Pool] = None,
        mo_profile: Optional[ManagedObjectProfile] = None,
        resource_group: Optional[ResourceGroup] = None,
        filter_no_ping: bool = False,
        profile_check_only: bool = False,
        failed_discovery_only: bool = False,
        filter_pending_links: bool = False,
        filter_none_problems: bool = False,
        filter_view_other: bool = False,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Union[str, int]]]:
        """
        Attrs:
            fields:
            pool: Requested Pool
            mo_profile: Requested Object Profile
            resource_group: Requested Device Resource Group
            filter_no_ping: Exclude unavailable devices
            profile_check_only: Request only SA Profile Check Rules
            failed_discovery_only: Exclude Diagnostic problem
            filter_pending_links: Exclude problem with topology methods
            filter_none_problems:
            filter_view_other:
            user: Requested user
        """
        if not pool:
            raise ValueError("'pool' parameter is required")
        if resource_group:
            mos = ManagedObject.objects.filter(
                effective_service_groups__overlap=ResourceGroup.get_nested_ids(resource_group)
            )
        else:
            mos = ManagedObject.objects.filter(pool=pool, is_managed=True)
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        if mo_profile:
            mos = mos.filter(object_profile=mo_profile)
        if filter_no_ping:
            mos = mos.filter(avail_status=True)
        if filter_view_other:
            mnp_in = list(ManagedObjectProfile.objects.filter(enable_ping=False))
            mos = mos.filter(profile=Profile.objects.get(name=GENERIC_PROFILE)).exclude(
                object_profile__in=mnp_in
            )
        if profile_check_only:
            match = {
                "$or": [
                    {"job.problems.suggest_cli": {"$exists": True}},
                    {"job.problems.suggest_snmp": {"$exists": True}},
                    {"job.problems.profile.": {"$regex": "Cannot detect profile"}},
                    {"job.problems.version.": {"$regex": "Remote error code 1000[1234]"}},
                ]
            }
        else:
            match = None
        exclude_method = []
        if filter_pending_links:
            exclude_method += ["lldp", "lacp", "cdp", "huawei_ndp"]
        mo_ids = list(mos.values_list("id", flat=True))
        row_num = 0
        pools = [Pool.get_by_id(p) for p in mos.values_list("pool", flat=True).distinct()]
        for p in pools:
            s = Scheduler("discovery", pool=p.name)
            coll = s.get_collection()
            for discovery in coll.with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED
            ).aggregate(cls.get_pipeline(mo_ids, match)):

                for method in [
                    x for x in discovery["job"][0]["problems"] if x not in exclude_method
                ]:
                    p = discovery["job"][0]["problems"][method]
                    if filter_none_problems and not p:
                        continue
                    row_num += 1
                    yield row_num, "managed_object_id", discovery["key"]
                    yield row_num, "last_success_discovery", (
                        discovery["st"].strftime("%d.%m.%Y %H:%M") if "st" in discovery else ""
                    )
                    yield row_num, "discovery", method
                    yield row_num, "error", cls.clean_problem(p)
