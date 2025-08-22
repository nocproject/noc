# ----------------------------------------------------------------------
# objectserialds datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Any, AsyncIterable, Dict, Iterable, List, Optional, Tuple

# Third-party modules
from django.db import connection

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
        FieldInfo(name="serial_moattr"),
        FieldInfo(name="serial_odata"),
    ]

    @classmethod
    def get_mo_attrs(cls) -> Dict[id, Tuple]:
        """
        Get data for keys listed in `attr_dict`, such as `Serial Number`
        from Postgres database table `sa_managedobjectattribute`
        """
        BASE_QUERY = "select managed_object_id, %s from sa_managedobjectattribute"
        KEY_SECTION = "case when key = '%s' then value else null end as %s"
        attr_dict = {
            "Serial Number": "serial_number",
            "HW version": "hw_version",
            "Boot PROM": "boot_prom",
            "Patch Version": "patch_version",
        }
        key_section = ", ".join([KEY_SECTION % (k, v) for k, v in attr_dict.items()])
        query = BASE_QUERY % key_section
        cursor = connection.cursor()
        cursor.execute(query)
        res = {}
        for mo_id, *r in cursor:
            res[mo_id] = (r[0], r[1], r[2], r[3])
        return res

    @classmethod
    def get_odata_serials(cls, mo_ids) -> Dict[id, str]:
        """
        Get serial numbers data from `data` field in `inv.Object` model
        """
        res = {}
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
            mo_id = o["managed_object"][0]["value"]
            serial = o["serial"][0]["value"]
            res[mo_id] = serial
        return res

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
        print("len(mo_ids)", len(mo_ids))
        mo_attrs = cls.get_mo_attrs()
        print("len(mo_attrs)", len(mo_attrs))
        odata_serials = cls.get_odata_serials(mo_ids)
        print("len(odata_serials)", len(odata_serials))
        row_num = 0
        for mo_id in mo_ids:
            row_num += 1
            yield row_num, "managed_object_id", mo_id
            attrs = mo_attrs.get(mo_id, None)
            serial = attrs[0] if attrs else None
            yield row_num, "serial_moattr", serial
            yield row_num, "serial_odata", odata_serials.get(mo_id, None)
