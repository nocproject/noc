# ----------------------------------------------------------------------
# LinkDetail Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable, Union, List

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from .base import FieldInfo, FieldType, ParamInfo, BaseDataSource
from noc.core.mongo.connection import get_db
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.platform import Platform
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.managedobject import ManagedObject


class LinkDetailDS(BaseDataSource):
    name = "linkdetailds"

    params = [
        ParamInfo(name="resource_group", type="str", model="inv.ResourceGroup"),
        ParamInfo(name="segment", type="str", model="inv.NetworkSegment"),
    ]

    fields = [
        FieldInfo(name="object1_admin_domain"),
        FieldInfo(name="object1_name"),
        FieldInfo(name="object1_address"),
        FieldInfo(name="object1_platform"),
        FieldInfo(name="object1_segment"),
        FieldInfo(name="object1_tags"),
        FieldInfo(name="object1_iface"),
        FieldInfo(name="object1_descr"),
        FieldInfo(name="object1_speed", type=FieldType.UINT),
        FieldInfo(name="object2_admin_domain"),
        FieldInfo(name="object2_name"),
        FieldInfo(name="object2_address"),
        FieldInfo(name="object2_platform"),
        FieldInfo(name="object2_segment"),
        FieldInfo(name="object2_tags"),
        FieldInfo(name="object2_iface"),
        FieldInfo(name="object2_descr"),
        FieldInfo(name="object2_speed", type=FieldType.UINT),
        FieldInfo(name="link_proto"),
        FieldInfo(name="last_seen"),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        resource_group: Optional[ResourceGroup] = None,
        segment: Optional[NetworkSegment] = None,
        admin_domain_ads: Optional[List[int]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Union[str, int]]]:
        def get_platform(id):
            return str(Platform.get_by_id(id)) if id else ""

        def get_segment(id):
            return str(NetworkSegment.get_by_id(id)) if id else ""

        # filter by incoming parameters
        mos = ManagedObject.objects.all()
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        if resource_group:
            mos = mos.filter(
                effective_service_groups__overlap=ResourceGroup.get_nested_ids(resource_group)
            )
        if segment:
            mos = mos.filter(segment__in=segment.get_nested_ids())
        mos_id = list(mos.values_list("id", flat=True))
        # prepare data to resolve referencing fields
        mo_resolv = {
            mo[0]: mo[1:]
            for mo in ManagedObject.objects.filter().values_list(
                "id",
                "administrative_domain__name",
                "name",
                "address",
                "platform",
                "segment",
                "labels",
            )
        }
        # main query
        match = {"int.managed_object": {"$in": mos_id}}
        group = {
            "_id": "$_id",
            "links": {
                "$push": {
                    "iface_n": "$int.name",
                    "iface_id": "$int._id",
                    "iface_descr": "$int.description",
                    "iface_speed": "$int.in_speed",
                    "dis_method": "$discovery_method",
                    "last_seen": "$last_seen",
                    "mo": "$int.managed_object",
                }
            },
        }
        data = (
            get_db()["noc.links"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [
                    {"$unwind": "$interfaces"},
                    {
                        "$lookup": {
                            "from": "noc.interfaces",
                            "localField": "interfaces",
                            "foreignField": "_id",
                            "as": "int",
                        }
                    },
                    {"$match": match},
                    {"$group": group},
                ],
                allowDiskUse=True,
            )
        )
        row_num = 0
        for row in data:
            if len(row["links"]) != 2:
                # Multilink or bad link
                continue
            s1, s2 = row["links"]
            s1mo, s2mo = s1["mo"][0], s2["mo"][0]
            row_num += 1
            yield row_num, "object1_admin_domain", mo_resolv[s1mo][0]
            yield row_num, "object1_name", mo_resolv[s1mo][1]
            yield row_num, "object1_address", mo_resolv[s1mo][2]
            yield row_num, "object1_platform", get_platform(mo_resolv[s1mo][3])
            yield row_num, "object1_segment", get_segment(mo_resolv[s1mo][4])
            yield row_num, "object1_tags", ";".join(mo_resolv[s1mo][5] or [])
            yield row_num, "object1_iface", s1["iface_n"][0]
            yield row_num, "object1_descr", (
                s1.get("iface_descr")[0] if s1.get("iface_descr") else ""
            )
            yield row_num, "object1_speed", s1.get("iface_speed")[0] if s1.get("iface_speed") else 0
            yield row_num, "object2_admin_domain", mo_resolv[s2mo][0]
            yield row_num, "object2_name", mo_resolv[s2mo][1]
            yield row_num, "object2_address", mo_resolv[s2mo][2]
            yield row_num, "object2_platform", get_platform(mo_resolv[s2mo][3])
            yield row_num, "object2_segment", get_segment(mo_resolv[s2mo][4])
            yield row_num, "object2_tags", ";".join(mo_resolv[s2mo][5] or [])
            yield row_num, "object2_iface", s2["iface_n"][0]
            yield row_num, "object2_descr", (
                s2.get("iface_descr")[0] if s2.get("iface_descr") else ""
            )
            yield row_num, "object2_speed", s2.get("iface_speed")[0] if s2.get("iface_speed") else 0
            yield row_num, "link_proto", s2.get("dis_method", "")
            yield row_num, "last_seen", s2.get("last_seen", "")
