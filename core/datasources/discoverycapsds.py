# ----------------------------------------------------------------------
# Discovery Caps Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.pool import Pool
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interface import Interface
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class DiscoveryCapsDS(BaseDataSource):
    name = "discoverycapsds"

    fields = [
        FieldInfo(name="managed_object"),
        FieldInfo(name="address"),
        FieldInfo(name="record_type"),
        FieldInfo(name="object"),
        FieldInfo(name="capabilities"),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        pool: Optional[Pool] = None,
        mo_profile: Optional[ManagedObjectProfile] = None,
        user: Optional[User] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        if not pool:
            raise ValueError("'pool' parameter is required")
        mos = ManagedObject.objects.filter(is_managed=True, pool=pool)
        if user and not user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(user))
        if mo_profile:
            mos = mos.filter(object_profile=mo_profile)
        row_num = 0
        for mo in mos:
            mo.get_caps()
            row_num += 1
            yield row_num, "managed_object", mo.name
            yield row_num, "address", mo.address
            yield row_num, "record_type", "mo"
            yield row_num, "object", _("Main")
            yield row_num, "capabilities", ",".join(mo.get_caps())
            for i in Interface.objects.filter(managed_object=mo):
                if i.type == "SVI":
                    continue
                row_num += 1
                yield row_num, "managed_object", mo.name
                yield row_num, "address", mo.address
                yield row_num, "record_type", "inf"
                yield row_num, "object", i.name
                yield row_num, "capabilities", ",".join(i.enabled_protocols)
