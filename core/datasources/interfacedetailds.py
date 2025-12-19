# ----------------------------------------------------------------------
# Interface Detail Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, AsyncIterable, Tuple, List

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from .base import FieldInfo, ParamInfo, FieldType, BaseDataSource
from noc.core.text import list_to_ranges
from noc.inv.models.interface import Interface
from noc.inv.models.interface import InterfaceProfile
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.managedobject import ManagedObject


class InterfaceDetailDS(BaseDataSource):
    name = "interfacedetailds"
    row_index = ("managed_object_id", "interface_name")
    params = [
        ParamInfo(name="iface_type", type="str", default="physical"),
        ParamInfo(name="iface_profile", type="str", model="inv.InterfaceProfile"),
        ParamInfo(name="resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="exclude_down", type="bool", default=False),
        ParamInfo(name="exclude_def_profile", type="bool", default=False),
        ParamInfo(name="only_admin_status", type="bool", default=False),
    ]
    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="interface_name"),
        FieldInfo(name="interface_description"),
        FieldInfo(name="interface_profile_name"),
        FieldInfo(name="type"),
        FieldInfo(name="mac_address"),
        FieldInfo(name="protocols", type=FieldType.LIST_STRING),
        FieldInfo(name="in_speed_h"),
        FieldInfo(name="admin_status", type=FieldType.BOOL),
        FieldInfo(name="oper_status", type=FieldType.BOOL),
        FieldInfo(name="oper_status_change", type=FieldType.DATETIME),
        FieldInfo(name="full_duplex", type=FieldType.BOOL),
        FieldInfo(name="untagged_vlan", type=FieldType.UINT),
        FieldInfo(name="tagged_vlans"),
        FieldInfo(name="is_uni", type=FieldType.BOOL),
    ]

    @staticmethod
    def humanize_speed(speed: Optional[int]) -> str:
        if not speed:
            return "-"
        for t, n in [(1000000, "G"), (1000, "M"), (1, "k")]:
            if speed >= t:
                if speed // t * t == speed:
                    return f"{speed // t}{n}"
                return f"{float(speed) / t:.2f}{n}"
        return str(speed)

    @staticmethod
    def parse_subs(subinterfaces):
        if subinterfaces:
            subinterface = subinterfaces[0]
            untagged = subinterface.get("untagged_vlan", 0)
            tagged = list_to_ranges(subinterface.get("tagged_vlans", []))
            return untagged, tagged
        return 0, ""

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        iface_type: str = "physical",
        iface_profile: Optional[InterfaceProfile] = None,
        resource_group: Optional[ResourceGroup] = None,
        exclude_down: bool = False,
        exclude_def_profile: bool = False,
        only_admin_status: bool = False,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        mos = ManagedObject.objects.filter(is_managed=True)
        if resource_group:
            mos = mos.filter(
                effective_service_groups__overlap=ResourceGroup.get_nested_ids(resource_group)
            )
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        mo_ids = list(mos.values_list("id", flat=True))
        match = {
            "managed_object": {"$in": mo_ids},
            "type": iface_type,
        }
        if iface_profile:
            match["profile"] = iface_profile.id
        if exclude_down:
            match["oper_status"] = True
        if exclude_def_profile and iface_profile is None:
            def_prof = [pr.id for pr in InterfaceProfile.objects.filter(name__contains="default")]
            match["profile"] = {"$nin": def_prof}
        if only_admin_status:
            match["admin_status"] = True
        row_num = 1
        for row in (
            Interface._get_collection()
            .with_options(
                read_preference=ReadPreference.SECONDARY_PREFERRED,
            )
            .aggregate(
                [
                    {"$match": match},
                    {
                        "$lookup": {
                            "from": "noc.subinterfaces",
                            "localField": "_id",
                            "foreignField": "interface",
                            "as": "subs",
                        }
                    },
                ]
            )
        ):
            ip = InterfaceProfile.get_by_id(row["profile"])
            if not ip:
                continue
            untagged_vlan, tagged_vlans = cls.parse_subs(row.get("subs"))
            speed = int(row.get("in_speed") or 0)
            yield row_num, "managed_object_id", int(row["managed_object"])
            yield row_num, "interface_name", row["name"]
            yield row_num, "interface_description", row.get("description") or ""
            yield row_num, "interface_profile_name", ip.name
            yield row_num, "type", row["type"]
            yield row_num, "mac_address", row.get("mac") or ""
            yield row_num, "protocols", row.get("enabled_protocols") or []
            yield row_num, "in_speed_h", cls.humanize_speed(speed)
            yield row_num, "admin_status", row.get("admin_status") or False
            yield row_num, "oper_status", row.get("oper_status") or False
            yield row_num, "oper_status_change", row.get("oper_status_change") or False
            yield row_num, "full_duplex", row.get("full_duplex") or False
            yield row_num, "untagged_vlan", untagged_vlan
            yield row_num, "tagged_vlans", tagged_vlans
            yield row_num, "is_uni", ip.is_uni
            row_num += 1
