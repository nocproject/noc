# ----------------------------------------------------------------------
# Managed Object Capabilities Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any, Tuple, List, AsyncIterable

# NOC modules
from .base import FieldInfo, BaseDataSource, FieldType
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.capability import Capability
from noc.core.validators import is_objectid


caps_dtype_map = {
    "bool": FieldType.BOOL,
    "str": FieldType.STRING,
    "int": FieldType.UINT,
    "float": FieldType.FLOAT,
    "strlist": FieldType.LIST_STRING,
}


def get_capabilities() -> Iterable[Tuple[str, str]]:
    for key, c_type, value, multi in (
        Capability.objects.filter().order_by("name").scalar("id", "type", "name", "multi")
    ):
        if multi:
            yield key, FieldType.LIST_STRING, value
        else:
            yield key, caps_dtype_map.get(c_type.value, FieldType.STRING), value


class ManagedObjectCapsDS(BaseDataSource):
    name = "managedobjectcapsds"
    row_index = "managed_object_id"

    fields = [FieldInfo(name="managed_object_id", type=FieldType.UINT), FieldInfo(name="all_caps")]

    @classmethod
    def iter_ds_fields(cls):
        yield from super().iter_ds_fields()
        for c_id, c_type, c_name in get_capabilities():
            yield FieldInfo(name=c_name, type=c_type, internal_name=str(c_id))

    @classmethod
    async def iter_caps(
        cls,
        caps: List[Dict[str, Any]],
        requested_caps: Dict[str, Any] = None,
        include_all: bool = False,
    ) -> AsyncIterable[Tuple[str, Any]]:
        """
        Consolidate capabilities list and return resulting dict of
        caps name -> caps value. First appearance of capability
        overrides later ones.
        Attrs:
            caps: Object Capabilities
            requested_caps: Requested Capabilities
            include_all: Include all_caps field
        """
        caps = {c["capability"]: c["value"] for c in caps}
        for cid, (f_name, f_default) in requested_caps.items():
            yield f_name, caps.get(cid, f_default)
        if include_all:
            yield "all_caps", ";".join(
                Capability.get_by_id(c).name for c in caps if Capability.get_by_id(c)
            )

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
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        q_caps = {}
        for f in cls.iter_ds_fields():
            c = (
                Capability.get_by_id(f.internal_name)
                if is_objectid(f.internal_name)
                else Capability.get_by_name(f.internal_name)
            )
            if not c:
                continue
            q_caps[str(c.id)] = (f.name, cls.get_caps_default(c))
        for num, (mo_id, caps) in enumerate(
            ManagedObject.objects.filter().values_list("id", "caps").iterator()
        ):
            yield num, "managed_object_id", mo_id
            async for c in cls.iter_caps(
                caps or [], requested_caps=q_caps, include_all="all_caps" in fields
            ):
                yield num, c[0], c[1]
