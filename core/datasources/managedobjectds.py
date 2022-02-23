# ----------------------------------------------------------------------
# ManagedObject Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any, List

# Third-party modules
import pandas as pd

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.capability import Capability
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.vendor import Vendor
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.authprofile import AuthProfile


class ManagedObjectDS(BaseDataSource):
    name = "managedobjectds"

    fields = [
        FieldInfo(name="id", description="Object Id", type="int64"),
        FieldInfo(name="name", description="Object Name"),
        # FieldInfo(name="hostname", description="Object Hostname"),
        # FieldInfo(name="status", description="Object Status"),
        FieldInfo(name="address", description="Object IP Address"),
        FieldInfo(name="vendor", description="Object Vendor"),
        FieldInfo(name="model", description="Object Model", internal_name="platform"),
        FieldInfo(name="sw_version", description="Object Firmware", internal_name="version"),
        # Attributes fields
        # FieldInfo(
        #     name="attr_hwversion", description="Object HW Version Attribute", internal_name="attrs"
        # ),
        # FieldInfo(
        #     name="attr_bootprom", description="Object Boot Prom Attribute", internal_name="attrs"
        # ),
        # FieldInfo(name="attr_patch", description="Object Patch Attribute", internal_name="attrs"),
        # FieldInfo(
        #     name="attr_serialnumber",
        #     description="Object Serial Number Attribute",
        #     internal_name="attrs",
        # ),
        # Location Fields
        FieldInfo(
            name="administrativedomain",
            description="Object Administrative Domain",
            internal_name="administrative_domain__name",
        ),
        FieldInfo(
            name="container",
            description="Object Container Name",
        ),
        FieldInfo(
            name="segment",
            description="Object Segment Name",
        ),
        FieldInfo(
            name="project",
            description="Object Segment Name",
        ),
        FieldInfo(
            name="auth_profile",
            description="Object Authentication Profile",
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
    def get_caps(cls, *args: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate capabilities list and return resulting dict of
        caps name -> caps value. First appearance of capability
        overrides later ones.

        :param args:
        :return:
        """
        r: Dict[str, Any] = {}
        for caps in args:
            for ci in caps:
                cn = Capability.get_by_id(ci["capability"])
                if cn in r:
                    continue
                r[cn.name] = ci["value"]
        return r

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields, with_index=True)]
        return pd.DataFrame.from_records(data, index="id")

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        fields = set(fields or [])
        q_fields = [f.internal_name or f.name for f in cls.fields if not fields or f.name in fields]
        if "with_index" in kwargs:
            q_fields += ["id"]
        for mo in ManagedObject.objects.values(*q_fields):
            if "caps" in mo:
                caps = cls.get_caps(mo.pop("caps"))
            else:
                caps = {}
            if "links" in mo:
                links = mo.pop("links")
                mo["link_count"] = len(links)
            if not fields or "physical_iface_count" in fields:
                mo["physical_iface_count"] = caps.get("DB | Interfaces", 0)
            if "platform" in mo:
                platform = mo.pop("platform")
                mo["model"] = Platform.get_by_id(platform).name if platform else ""
            if "sw_version" in mo:
                sw_version = mo.pop("sw_version")
                mo["version"] = Firmware.get_by_id(sw_version).version if sw_version else ""
            if "vendor" in mo:
                mo["vendor"] = Vendor.get_by_id(mo["vendor"]).name if mo["vendor"] else ""
            if "auth_profile" in mo:
                mo["auth_profile"] = (
                    AuthProfile.get_by_id(mo["auth_profile"]).name if mo["auth_profile"] else ""
                )
            if "segment" in mo:
                mo["segment"] = (
                    NetworkSegment.get_by_id(mo["segment"]).name if mo["segment"] else ""
                )
            if "administrative_domain__name" in mo:
                mo["administrative_domain"] = mo.pop("administrative_domain__name")
            yield mo
