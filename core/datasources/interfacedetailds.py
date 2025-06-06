# ----------------------------------------------------------------------
# Interface Detail Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, AsyncIterable, Tuple, List

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from .base import FieldInfo, ParamInfo, FieldType, BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.interface import InterfaceProfile


class InterfaceDetailDS(BaseDataSource):
    name = "interfacedetailds"

    row_index = ("managed_object_id", "interface_name")

    params = [ParamInfo(name="iface_type", type="str", default="physical")]

    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="interface_name"),
        FieldInfo(name="interface_description"),
        FieldInfo(name="interface_profile_name"),
        FieldInfo(name="type"),
        FieldInfo(name="mac_address"),
        FieldInfo(name="protocols", type=FieldType.LIST_STRING),
        # FieldInfo(name="in_speed", type=FieldType.UINT64),
        FieldInfo(name="in_speed_h"),
        FieldInfo(name="admin_status", type=FieldType.BOOL),
        FieldInfo(name="oper_status", type=FieldType.BOOL),
        FieldInfo(name="oper_status_change", type=FieldType.DATETIME),
        FieldInfo(name="full_duplex", type=FieldType.BOOL),
        FieldInfo(name="untagged_vlan", type=FieldType.UINT),
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
                else:
                    return f"{float(speed) / t:.2f}{n}"
        return str(speed)

    @staticmethod
    def parse_subs(subinterfaces):
        if not subinterfaces or "untagged_vlan" not in subinterfaces[0]:
            return 0
        return subinterfaces[0]["untagged_vlan"]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        iface_type: str = "physical",
        managed_object_ids: Optional[List[int]] = None,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        """ """
        coll = Interface._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED,
        )
        match = {"type": iface_type}
        mos_ex = frozenset(
            ManagedObject.objects.filter(is_managed=False).values_list("id", flat=True)
        )
        if admin_domain_ads:
            managed_object_ids = frozenset(
                ManagedObject.objects.filter(
                    administrative_domain__in=admin_domain_ads,
                ).values_list("id", flat=True)
            )
        if managed_object_ids:
            match["managed_object"] = {"$in": list(managed_object_ids - mos_ex)}
        elif mos_ex:
            match["managed_object"] = {"$nin": list(mos_ex)}
        lookup = {
            "from": "noc.subinterfaces",
            "localField": "_id",
            "foreignField": "interface",
            "as": "subs",
        }
        for row_num, row in enumerate(
            coll.aggregate(
                [
                    {"$match": match},
                    {"$lookup": lookup},
                    {"$sort": {"managed_object": 1, "name": 1}},
                ]
            )
        ):
            ip = InterfaceProfile.get_by_id(row["profile"])
            if not ip:
                continue
            untagged_vlan = cls.parse_subs(row.get("subs"))
            speed = int(row.get("in_speed") or 0)
            yield row_num, "managed_object_id", int(row["managed_object"])
            yield row_num, "interface_name", row["name"]
            yield row_num, "interface_description", row.get("description") or ""
            yield row_num, "interface_profile_name", ip.name
            yield row_num, "type", row["type"]
            yield row_num, "mac_address", row.get("mac") or ""
            yield row_num, "protocols", row.get("enabled_protocols") or []
            # yield row_num, "in_speed", int(row.get("in_speed") or 0)
            yield row_num, "in_speed_h", cls.humanize_speed(speed)
            yield row_num, "admin_status", row.get("admin_status") or False
            yield row_num, "oper_status", row.get("oper_status") or False
            yield row_num, "oper_status_change", row.get("oper_status_change") or False
            yield row_num, "full_duplex", row.get("full_duplex") or False
            yield row_num, "untagged_vlan", untagged_vlan
            yield row_num, "is_uni", ip.is_uni
