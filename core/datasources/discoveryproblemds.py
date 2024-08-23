# ----------------------------------------------------------------------
# Discovery Problem Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.core.mongo.connection import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.sa.models.profile import GENERIC_PROFILE
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _

CODE_MAP = {
    "1": "Unknown error",
    "10000": "Unspecified CLI error",
    "10005": "Connection refused",
    "10001": "Authentication failed",
    "10002": "No super command defined",
    "10003": "No super privileges",
    "10004": "SSH Protocol error",
}


class ReportDiscoveryProblem(object):
    """Class for get list of discovery problems"""

    def __init__(self, mos, avail_only=False, match=None):
        """

        :param mos:
        :type mos: ManagedObject.objects.filter()
        """
        self.mo_ids = list(mos.values_list("id", flat=True))
        if avail_only:
            status = ManagedObject.get_statuses(self.mo_ids)
            self.mo_ids = [s for s in status if status[s]]
        self.mos_pools = [Pool.get_by_id(p) for p in set(mos.values_list("pool", flat=True))]
        self.coll_name = "noc.schedules.discovery.%s"
        # @todo Good way for pipelines fill
        self.pipelines = {}
        self.match = match

    def pipeline(self):
        """
        Generate pipeline for request
        :return:
        :rtype: list
        """
        discovery = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
        pipeline = [
            {"$match": {"key": {"$in": self.mo_ids}, "jcls": discovery}},
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
        if self.match:
            # @todo check match
            pipeline += [{"$match": self.match}]
        else:
            pipeline += [{"$match": {"job.problems": {"$exists": True, "$ne": {}}}}]
        return pipeline

    def __iter__(self):
        for p in self.mos_pools:
            r = (
                get_db()[self.coll_name % p.name]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(self.pipelines.get(p.name, self.pipeline()))
            )
            for x in r:
                # @todo Append info for MO
                yield x


class DiscoveryProblemDS(BaseDataSource):
    name = "discoveryproblemds"

    fields = [
        FieldInfo(name="managed_object"),
        FieldInfo(name="address"),
        FieldInfo(name="profile"),
        FieldInfo(name="domain"),
        FieldInfo(name="avail"),
        FieldInfo(name="last_success_discovery"),
        FieldInfo(name="discovery"),
        FieldInfo(name="error"),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, user=None, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        if "pool" not in kwargs:
            raise ValueError("'pool' parameter is required")
        pool = kwargs.get("pool")
        mo_profile = kwargs.get("mo_profile")
        resource_group = kwargs.get("resource_group")
        filter_no_ping = "filter_no_ping" in kwargs
        profile_check_only = "profile_check_only" in kwargs
        failed_discovery_only = "failed_discovery_only" in kwargs
        filter_pending_links = "filter_pending_links" in kwargs
        filter_none_problems = "filter_none_problems" in kwargs
        filter_view_other = "filter_view_other" in kwargs

        match = None
        if resource_group:
            mos = ManagedObject.objects.filter(
                effective_service_groups__overlap=ResourceGroup.get_nested_ids(resource_group)
            )
        else:
            mos = ManagedObject.objects.filter(pool=pool, is_managed=True)
        if user and not user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(user))
        if mo_profile:
            mos = mos.filter(object_profile=mo_profile)
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
        elif failed_discovery_only:
            match = {
                "$and": [
                    {"job.problems": {"$exists": "true", "$ne": {}}},
                    {"job.problems.suggest_snmp": {"$exists": False}},
                    {"job.problems.suggest_cli": {"$exists": False}},
                ]
            }
        elif filter_view_other:
            match = {"job.problems.suggest_snmp": {"$exists": False}}
        rdp = ReportDiscoveryProblem(mos, avail_only=filter_no_ping, match=match)
        exclude_method = []
        if filter_pending_links:
            exclude_method += ["lldp", "lacp", "cdp", "huawei_ndp"]
        row_num = 0
        for discovery in rdp:
            mo = ManagedObject.get_by_id(discovery["key"])
            for method in [x for x in discovery["job"][0]["problems"] if x not in exclude_method]:
                problem = discovery["job"][0]["problems"][method]
                if filter_none_problems and not problem:
                    continue
                if isinstance(problem, dict) and "" in problem:
                    problem = problem.get("", "")
                if "Remote error code" in problem:
                    problem = CODE_MAP.get(problem.split(" ")[-1], problem)
                if isinstance(problem, str):
                    problem = problem.replace("\n", " ").replace("\r", " ")
                row_num += 1
                yield row_num, "managed_object", mo.name
                yield row_num, "address", mo.address
                yield row_num, "profile", mo.profile.name
                yield row_num, "domain", mo.administrative_domain.name
                yield row_num, "avail", _("Yes") if mo.get_status() else _("No")
                yield row_num, "last_success_discovery", (
                    discovery["st"].strftime("%d.%m.%Y %H:%M") if "st" in discovery else ""
                )
                yield row_num, "discovery", method
                yield row_num, "error", problem
