# ----------------------------------------------------------------------
# ManagedObject Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any

# Third-party modules
import pandas as pd

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.platform import Platform


class ManagedObjectDS(BaseDataSource):
    name = "managedobjectds"

    fields = [
        FieldInfo(name="id", description="ManagedObject Id", type="int64"),
        FieldInfo(name="name", description="ManagedObject Name"),
        FieldInfo(name="address", description="ManagedObject IP Address"),
        FieldInfo(name="model", description="ManagedObject Model", internal_name="platform"),
        FieldInfo(name="version", description="ManagedObject Firmware"),
        FieldInfo(
            name="administrativedomain",
            description="ManagedObject Administrative Domain",
            internal_name="administrative_domain__name",
        ),
        FieldInfo(
            name="link_count",
            description="ManagedObject links count",
            internal_name="links",
            type="int64",
        ),
        FieldInfo(
            name="physical_iface_count",
            description="ManagedObject physical interfaces",
            internal_name="caps",
            type="int64",
        ),
    ]

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields, with_index=True)]
        return pd.DataFrame.from_records(data, index="id")

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        fields = set(fields or [])
        q_fields = [
            f.internal_name or f.name
            for f in cls.fields
            if not fields or f.name in fields or f.internal_name in fields
        ]
        if "with_index" in kwargs:
            q_fields += ["id"]
        print(q_fields)
        for mo in ManagedObject.objects.values(*q_fields):
            if "caps" in mo:
                caps = mo.pop("caps")
            if "links" in mo:
                links = mo.pop("links")
                mo["link_count"] = len(links)
            if "physical_iface_count" in fields:
                mo["physical_iface_count"] = 0
            if "platform" in mo:
                platform = mo.pop("platform")
                mo["model"] = Platform.get_by_id(platform).name if platform else ""
            if "administrative_domain__name" in mo:
                mo["administrative_domain"] = mo.pop("administrative_domain__name")
            yield mo
