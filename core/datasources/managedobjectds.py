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
from noc.sa.models.authprofile import AuthProfile
from noc.sa.models.profile import Profile
from noc.inv.models.capability import Capability
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.vendor import Vendor
from noc.inv.models.networksegment import NetworkSegment
from noc.project.models.project import Project


class ManagedObjectDS(BaseDataSource):
    name = "managedobjectds"

    fields = [
        FieldInfo(name="id", description="Object Id", type="int64"),
        FieldInfo(name="name", description="Object Name"),
        FieldInfo(name="profile", description="Profile Name"),
        FieldInfo(
            name="object_profile",
            description="Object Profile Name",
            internal_name="object_profile__name",
        ),
        # FieldInfo(name="hostname", description="Object Hostname"),
        # FieldInfo(name="status", description="Object Status"),
        FieldInfo(name="address", description="Object IP Address"),
        FieldInfo(name="vendor", description="Object Vendor"),
        FieldInfo(name="model", description="Object Model", internal_name="platform"),
        FieldInfo(name="sw_version", description="Object Firmware", internal_name="version"),
        # Attributes fields
        FieldInfo(name="attr_hwversion", description="Object HW Version Attribute"),
        FieldInfo(name="attr_bootprom", description="Object Boot Prom Attribute"),
        FieldInfo(name="attr_patch", description="Object Patch Attribute"),
        FieldInfo(
            name="attr_serialnumber",
            description="Object Serial Number Attribute",
        ),
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

    ATTR_QUERY = """
    SELECT value
    FROM sa_managedobjectattribute
    WHERE key='%s' AND managed_object_id=sa_managedobject.id
    """

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
        mos = ManagedObject.objects.filter()
        extra_select = {}
        if not fields or "attr_hwversion" in fields:
            extra_select["attr_hwversion"] = cls.ATTR_QUERY % "HW version"
        if not fields or "attr_bootprom" in fields:
            extra_select["attr_bootprom"] = cls.ATTR_QUERY % "Boot PROM"
        if not fields or "attr_patch" in fields:
            extra_select["attr_patch"] = cls.ATTR_QUERY % "Patch Version"
        if not fields or "attr_serialnumber" in fields:
            extra_select["attr_serialnumber"] = cls.ATTR_QUERY % "Serial Number"
        if extra_select:
            mos = mos.extra(select=extra_select)
        for mo in mos.values(*q_fields):
            if "caps" in mo:
                caps = cls.get_caps(mo.pop("caps"))
            else:
                caps = {}
            if "links" in mo:
                links = mo.pop("links")
                mo["link_count"] = len(links)
            if not fields or "physical_iface_count" in fields:
                mo["physical_iface_count"] = caps.get("DB | Interfaces", 0)
            if "profile" in mo:
                mo["profile"] = Profile.get_by_id(mo["profile"]).name if mo["profile"] else ""
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
            if "object_profile__name" in mo:
                mo["object_profile"] = mo.pop("object_profile__name")
            if "project" in mo:
                mo["project"] = Project.get_by_id(mo["project"]).name if mo["project"] else ""
            yield mo
