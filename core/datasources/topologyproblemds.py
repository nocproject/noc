# ----------------------------------------------------------------------
# Topology Problems DataSource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import AsyncIterable, Dict, List, Optional, Iterable, Tuple

# NOC modules
from noc.core.profile.loader import GENERIC_PROFILE as GENERIC_PROFILE_NAME
from noc.core.translation import ugettext as _
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.profile import Profile
from .base import FieldInfo, FieldType, BaseDataSource, ParamInfo

GENERIC_PROFILE = Profile.get_by_name(GENERIC_PROFILE_NAME)


class TopologyProblemDS(BaseDataSource):
    name = "topologyproblemds"
    row_index = "managed_object_id"
    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="problem"),
    ]
    params = [
        ParamInfo(name="pool", type="str", model="main.Pool", required=True),
        ParamInfo(name="mo_profile", type="int", model="sa.ManagedObjectProfile"),
        ParamInfo(name="available_only", type="bool", default=False),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        pool: Optional[Pool] = None,
        mo_profile: Optional[ManagedObjectProfile] = None,
        available_only: bool = False,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        problems: Dict[int, str] = {}  # mo_id -> problem
        mos = ManagedObject.objects.filter(is_managed=True, pool=pool)
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        if mo_profile:
            mos = mos.filter(object_profile=mo_profile)
        mos_set = {mo.id for mo in mos}
        if available_only:
            statuses = ManagedObject.get_statuses(list(mos_set))
            mos_set = {mo_id for mo_id in mos_set if statuses.get(mo_id)}
        # Get all managed objects with generic profile
        for mo in mos:
            if mo.id not in mos_set:
                continue
            if mo.profile == GENERIC_PROFILE:
                problems[mo.id] = _("Profile check failed")
        # Get all managed objects without interfaces
        if_mo = {
            iface["_id"]: iface.get("managed_object")
            for iface in Interface._get_collection().find({}, {"_id": 1, "managed_object": 1})
        }
        for mo_id in mos_set - set(problems) - set(if_mo.values()):
            problems[mo_id] = _("No interfaces")
        # Get all managed objects without links
        linked_mos = set()
        for d in Link._get_collection().find({}):
            for i in d["interfaces"]:
                linked_mos.add(if_mo.get(i))
        for mo_id in mos_set - set(problems) - linked_mos:
            problems[mo_id] = _("No links")
        # Get all managed objects without uplinks
        uplinks = {}
        for mo_id, mo_uplinks in ManagedObject.objects.filter().values_list("id", "uplinks"):
            nu = len(mo_uplinks or [])
            if nu:
                uplinks[mo_id] = nu
        for mo_id in mos_set - set(problems) - set(uplinks):
            problems[mo_id] = _("No uplinks")
        num = 1
        for mo_id, problem in problems.items():
            yield num, "managed_object_id", mo_id
            yield num, "problem", problem
            num += 1
