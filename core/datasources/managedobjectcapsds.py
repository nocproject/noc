# ----------------------------------------------------------------------
# Managed Object Capabilities Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any, Tuple

# Third-party modules
import pandas as pd

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.capability import Capability


def get_capabilities() -> Iterable[Tuple[str, str]]:
    for key, c_type, value in (
        Capability.objects.filter().order_by("name").scalar("id", "type", "name")
    ):
        yield key, c_type, value


class ManagedObjectCapsDS(BaseDataSource):
    name = "managedobjectcapsds"

    fields = [FieldInfo(name="managed_object_id", type="int")] + [
        FieldInfo(name=c_name, type=c_type, internal_name=str(c_id))
        for c_id, c_type, c_name in get_capabilities()
    ]

    @classmethod
    def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        ## df = pd.DataFrame(index="managed_object_id", columns=[ff.name for ff in cls.fields if not fields or ff.name in fields or ff.name == "managed_object_id"])
        ## for rr in cls.iter_query(fields, require_index=True):
        ##     df.loc[df.shape[0], :] = rr
        ## return df
        # data = [mm for mm in cls.iter_query(fields, require_index=True)]
        data = pd.DataFrame.from_records(
            cls.iter_query(fields, require_index=True),
            index="managed_object_id",
            columns=[
                ff.name
                for ff in cls.fields
                if not fields or ff.name in fields or ff.name == "managed_object_id"
            ],
        )
        return data

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
    def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        query_fields = [ff.name for ff in cls.fields[1:] if not fields or ff.name in fields]
        resolve_caps = {ff.internal_name: ff.name for ff in cls.fields[1:]}
        convert_type_caps = {ff.name: ff.type for ff in cls.fields[1:]}
        for mo_id, caps in ManagedObject.objects.filter().values_list("id", "caps").iterator():
            caps = {resolve_caps[ff["capability"]]: ff["value"] for ff in caps}
            r = {ff: cls.clean_value(convert_type_caps[ff], caps.get(ff)) for ff in query_fields}
            r["managed_object_id"] = mo_id
            yield r
