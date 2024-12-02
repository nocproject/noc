# ----------------------------------------------------------------------
# Interface Detail Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, AsyncIterable, Tuple, List

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.inv.models.interface import Interface
from noc.inv.models.interface import InterfaceProfile


class InterfaceDetailDS(BaseDataSource):
    name = "interfacedetailds"

    row_index = ("managed_object_id", "interface_name")

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

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        iface_type: str = "physical",
        managed_object_ids: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        """ """
        coll = Interface._get_collection()
        f = {"type": iface_type}
        if managed_object_ids:
            f["managed_object"] = {"$in": managed_object_ids}
        for row_num, row in enumerate(coll.find(f).sort([("managed_object", 1), ("name", 1)])):
            ip = InterfaceProfile.get_by_id(row["profile"])
            if not ip:
                continue
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
            yield row_num, "is_uni", ip.is_uni
