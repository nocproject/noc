# ----------------------------------------------------------------------
# objectserialds datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Any, AsyncIterable, Iterable, List, Optional, Tuple

# NOC modules
from .base import BaseDataSource, FieldInfo, FieldType
from noc.inv.models.object import Object
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.managedobject import ManagedObject


class ObjectSerialDS(BaseDataSource):
    name = "objectserialds"
    row_index = "managed_object_id"

    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="serial"),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        admin_domain_ads: Optional[List[int]] = None,
        resource_group: Optional[ResourceGroup] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Any]]:
        mos = ManagedObject.objects
        if admin_domain_ads:
            mos = mos.filter(administrative_domain__in=admin_domain_ads)
        mos = mos.filter(
            effective_service_groups__overlap=ResourceGroup.get_nested_ids(resource_group)
        )
        mo_ids = [x["id"] for x in mos.values("id")]
        row_num = 0
        for o in Object._get_collection().aggregate(
            [
                {
                    "$match": {
                        "data": {"$elemMatch": {"attr": "managed_object", "value": {"$in": mo_ids}}}
                    }
                },
                {
                    "$project": {
                        "managed_object": {
                            "$filter": {
                                "input": "$data",
                                "cond": {"$eq": ["$$this.attr", "managed_object"]},
                            }
                        },
                        "serial": {
                            "$filter": {
                                "input": "$data",
                                "cond": {"$eq": ["$$this.attr", "serial"]},
                            }
                        },
                    }
                },
                {"$match": {"managed_object": {"$size": 1}, "serial": {"$size": 1}}},
            ]
        ):
            row_num += 1
            yield row_num, "managed_object_id", o["managed_object"][0]["value"]
            yield row_num, "serial", o["serial"][0]["value"]
