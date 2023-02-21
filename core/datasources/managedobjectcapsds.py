# ----------------------------------------------------------------------
# Managed Object Capabilities Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, AsyncIterable, Tuple

# Third-party modules
import pandas as pd

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.capability import Capability


caps_dtype_map = {
    "bool": FieldType.BOOL,
    "str": FieldType.STRING,
    "int": FieldType.UINT,
    "float": FieldType.FLOAT,
}


def get_capabilities() -> Iterable[Tuple[str, str]]:
    for key, c_type, value in (
        Capability.objects.filter().order_by("name").scalar("id", "type", "name")
    ):
        yield key, caps_dtype_map[c_type], value


class ManagedObjectCapsDS(BaseDataSource):
    name = "managedobjectcapsds"
    row_index = "managed_object_id"

    fields = [FieldInfo(name="managed_object_id", type="int")] + [
        FieldInfo(name=c_name, type=c_type, internal_name=str(c_id))
        for c_id, c_type, c_name in get_capabilities()
    ]

    @classmethod
    def chunk_query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        CHUNK = 10000
        columns = [
            ff.name
            for ff in cls.fields
            if not fields or ff.name in fields or ff.name == "managed_object_id"
        ]
        data = []
        next_chunk = CHUNK
        result = pd.DataFrame.from_records(
            [],
            index="managed_object_id",
            columns=columns,
        )
        for num, row in enumerate(cls.iter_query(fields, require_index=True)):
            data.append(row)
            if len(data) // next_chunk == 1:
                result = pd.concat(
                    [
                        result,
                        pd.DataFrame.from_records(
                            data,
                            index="managed_object_id",
                            columns=columns,
                        ),
                    ],
                    copy=False,
                )
                data = []
                next_chunk += CHUNK
        if data:
            result = pd.concat(
                [
                    result,
                    pd.DataFrame.from_records(
                        data,
                        index="managed_object_id",
                        columns=columns,
                    ),
                ],
                copy=False,
            )
        return result

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        query_fields = [ff.name for ff in cls.fields[1:] if not fields or ff.name in fields]
        resolve_caps = {ff.internal_name: ff.name for ff in cls.fields[1:]}
        convert_type_caps = {ff.name: ff.type for ff in cls.fields[1:]}
        row_num = 0
        for mo_id, caps in ManagedObject.objects.filter().values_list("id", "caps").iterator():
            caps = {resolve_caps[ff["capability"]]: ff["value"] for ff in caps}
            row_num += 1
            for ff in query_fields:
                yield row_num, ff, cls.clean_value(convert_type_caps[ff], caps.get(ff))
            yield row_num, "managed_object_id", mo_id
