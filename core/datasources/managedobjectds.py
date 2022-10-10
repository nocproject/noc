# ----------------------------------------------------------------------
# ManagedObject Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any, List, Tuple, Set

# Third-party modules
import pandas as pd
from pymongo.read_preferences import ReadPreference

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.authprofile import AuthProfile
from noc.sa.models.profile import Profile
from noc.sa.models.objectstatus import ObjectStatus
from noc.inv.models.capability import Capability
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.vendor import Vendor
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.discoveryid import DiscoveryID
from noc.project.models.project import Project


def get_capabilities() -> Iterable[Tuple[str, str]]:
    for key, c_type, value in (
        Capability.objects.filter().order_by("name").scalar("id", "type", "name")
    ):
        yield key, c_type, value


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
        FieldInfo(name="hostname", description="Object Hostname", internal_name="id"),
        FieldInfo(
            name="status",
            description="Object Admin Status",
            type="bool",
            internal_name="is_managed",
        ),
        FieldInfo(name="address", description="Object IP Address"),
        # Inventory fields
        FieldInfo(name="vendor", description="Object Vendor"),
        FieldInfo(name="model", description="Object Model", internal_name="platform"),
        FieldInfo(name="sw_version", description="Object Firmware", internal_name="version"),
        # Attributes fields
        FieldInfo(
            name="attr_hwversion",
            description="Object HW Version Attribute",
            internal_name="Chassis | HW Version",
        ),
        FieldInfo(
            name="attr_bootprom",
            description="Object Boot Prom Attribute",
            internal_name="Chassis | Boot PROM",
        ),
        FieldInfo(
            name="attr_patch",
            description="Object Patch Attribute",
            internal_name="Software | Patch Version",
        ),
        FieldInfo(
            name="attr_serialnumber",
            description="Object Serial Number Attribute",
            internal_name="Chassis | Serial Number",
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
        # Stat fields
        FieldInfo(
            name="link_count",
            description="Object links count",
            internal_name="links",
            type="int64",
        ),
        FieldInfo(
            name="physical_iface_count",
            description="Object physical interfaces",
            internal_name="DB | Interfaces",
            type="int64",
        ),
        # Oper fields
        FieldInfo(
            name="avail",
            description="Object Availability Status",
            internal_name="id",
            type="bool",
        ),
    ] + [
        FieldInfo(name=c_name, type=c_type, internal_name=str(c_id))
        for c_id, c_type, c_name in get_capabilities()
    ]

    @classmethod
    def get_caps(
        cls, *args: List[Dict[str, Any]], requested_caps: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Consolidate capabilities list and return resulting dict of
        caps name -> caps value. First appearance of capability
        overrides later ones.

        :param args:
        :param requested_caps:
        :return:
        """
        r: Dict[str, Any] = {}
        for ci in args[0]:
            cn = Capability.get_by_id(ci["capability"])
            if requested_caps and cn.name not in requested_caps:
                continue
            r[cn.name] = ci["value"]
        return r

    @staticmethod
    def get_caps_default(caps: Capability):
        """
        Capability field default value
        :param caps:
        :return:
        """
        if caps.type == "str":
            return ""
        elif caps.type == "int":
            return 0
        elif caps.type == "float":
            return 0.0
        return False

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields, *args, **kwargs)]
        return pd.DataFrame.from_records(data, index="id")

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        fields = set(fields or [])
        q_fields, q_caps = [], {}
        # Getting requested fields
        for f in cls.fields:
            if fields and f.name not in fields and f.name != "id":
                continue
            if "|" in f.name or (f.internal_name and "|" in f.internal_name) or f.name == "SNMP":
                c_name = f.name if "|" in f.name else f.internal_name
                c = Capability.get_by_name(c_name)
                q_caps[c_name] = cls.get_caps_default(c)
            else:
                q_fields.append(f.internal_name or f.name)
        if q_caps and "caps" not in q_fields:
            q_fields.append("caps")
        mos = ManagedObject.objects.filter()
        # Dictionaries
        hostname_map, segment_map, avail_map = {}, {}, {}
        # Lookup fields dictionaries
        if not fields or "hostname" in fields:
            hostname_map = {
                val["object"]: val["hostname"]
                for val in DiscoveryID._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .find({"hostname": {"$exists": 1}}, {"object": 1, "hostname": 1})
            }
        if not fields or "segment" in fields:
            segment_map = {
                str(n["_id"]): n["name"]
                for n in NetworkSegment._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .find({}, {"name": 1})
            }
        if not fields or "avail" in fields:
            avail_map = {
                val["object"]: val["status"]
                for val in ObjectStatus._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .find({"object": {"$exists": 1}}, {"object": 1, "status": 1})
            }
        # Main loop
        for mo in mos.values(*q_fields).iterator():
            mo.update(q_caps)
            iface_count = 0
            if "caps" in mo:
                caps = cls.get_caps(mo.pop("caps"), requested_caps=set(q_caps))
                mo.update(caps)
            else:
                caps = {}
            if not fields or "attr_hwversion" in fields:
                mo["attr_hwversion"] = caps.get("Chassis | HW Version", "")
            if not fields or "attr_bootprom" in fields:
                mo["attr_bootprom"] = caps.get("Chassis | Boot PROM", "")
            if not fields or "attr_patch" in fields:
                mo["attr_patch"] = caps.get("Software | Patch Version", "")
            if not fields or "attr_serialnumber" in fields:
                mo["attr_serialnumber"] = caps.get("Chassis | Serial Number", "")
            if "is_managed" in mo:
                mo["status"] = mo.pop("is_managed")
            if "links" in mo:
                links = mo.pop("links")
                mo["link_count"] = len(links)
            if not fields or "physical_iface_count" in fields:
                mo["physical_iface_count"] = caps.get("DB | Interfaces", iface_count)
            if "profile" in mo:
                mo["profile"] = Profile.get_by_id(mo["profile"]).name if mo["profile"] else None
            if "platform" in mo:
                platform = mo.pop("platform")
                mo["model"] = Platform.get_by_id(platform).name if platform else None
            if "sw_version" in mo:
                sw_version = mo.pop("sw_version")
                mo["version"] = Firmware.get_by_id(sw_version).version if sw_version else None
            if "vendor" in mo:
                mo["vendor"] = Vendor.get_by_id(mo["vendor"]).name if mo["vendor"] else None
            if hostname_map:
                mo["hostname"] = hostname_map.get(mo["id"])
            if segment_map:
                mo["segment"] = segment_map.get(mo["segment"])
            if avail_map:
                mo["avail"] = avail_map.get(mo["id"])
            if "auth_profile" in mo:
                mo["auth_profile"] = (
                    AuthProfile.get_by_id(mo["auth_profile"]).name if mo["auth_profile"] else None
                )
            if "administrative_domain__name" in mo:
                mo["administrative_domain"] = mo.pop("administrative_domain__name")
            if "object_profile__name" in mo:
                mo["object_profile"] = mo.pop("object_profile__name")
            if "project" in mo:
                mo["project"] = Project.get_by_id(mo["project"]).name if mo["project"] else None
            yield mo
