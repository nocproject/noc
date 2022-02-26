# ----------------------------------------------------------------------
# Managed Object Capabilities Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any, Tuple

# Third-party modules
import pandas as pd

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.capability import Capability


def get_capabilities() -> Iterable[Tuple[str, str]]:
    for key, value in Capability.objects.filter().order_by("name").scalar("id", "name"):
        yield key, value


class ManagedObjectCapsDS(BaseDataSource):
    name = "managedobjectcapsds"

    fields = [FieldInfo(name="managed_object_id", type="int64")] + [
        FieldInfo(name=c_name, type="bool", internal_name=str(c_id))
        for c_id, c_name in get_capabilities()
    ]

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields, require_index=True)]
        return pd.DataFrame.from_records(
            data, index="managed_object_id", columns=[ff.name for ff in cls.fields]
        )

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        query_fields = [ff.name for ff in cls.fields[1:]]
        resolve_caps = {ff.internal_name: ff.name for ff in cls.fields[1:]}
        for mo_id, caps in ManagedObject.objects.filter().values_list("id", "caps").iterator():
            caps = {resolve_caps[ff["capability"]]: ff["value"] for ff in caps}
            r = {ff: caps.get(ff) for ff in query_fields}
            r["managed_object_id"] = mo_id
            yield r
