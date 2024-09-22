# ----------------------------------------------------------------------
# Object Model Data Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, AsyncIterable, Tuple, Union

# NOC modules
from .base import FieldInfo, BaseDataSource, FieldType
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.modelinterface import ModelInterface


attrs_dtype_map = {
    "bool": FieldType.BOOL,
    "str": FieldType.STRING,
    "int": FieldType.UINT,
    "float": FieldType.FLOAT,
    "strlist": FieldType.LIST_STRING,
}

attrs_type_default_map = {
    "bool": False,
    "str": "",
    "int": 0,
    "float": 0.0,
    "strlist": [],
}


class ObjectModelDataDS(BaseDataSource):
    name = "objectmodeldatads"

    fields = [
        FieldInfo(name="object_model_id", type=FieldType.UINT),
        FieldInfo(name="vendor"),
        FieldInfo(name="vendor_id"),
        FieldInfo(name="name"),
        FieldInfo(name="ru"),
    ]

    @classmethod
    def iter_ds_fields(cls):
        yield from super().iter_ds_fields()
        for mi in ModelInterface.objects.filter():
            if not mi.attrs:
                continue
            for a in mi.attrs:
                if not a.is_const:
                    continue
                yield FieldInfo(
                    name=f"{mi.name}_{a.name}",
                    type=attrs_dtype_map[a.type],
                    internal_name=f"{mi.name}.{a.name}",
                )

    @staticmethod
    def clean_value(attr, value):
        if attr.type == "bool":
            return bool(value)
        if value is not None:
            return attr._clean(value)
        return attrs_type_default_map[attr.type]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        *args,
        managed_only: Optional[bool] = False,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Union[str, int]]]:
        """"""
        if managed_only:
            filters = {"data__match": {"interface": "management", "attr": "managed", "value": True}}
        else:
            filters = {}
        q_attrs = []
        for f in cls.iter_ds_fields():
            if not f.internal_name:
                continue
            iface, attr = f.internal_name.split(".")
            q_attrs.append((iface, ModelInterface.get_interface_attr(iface, attr)))
        for row_num, m in enumerate(ObjectModel.objects.filter(**filters)):
            yield row_num, "object_model_id", str(m.id)
            yield row_num, "vendor_id", str(m.vendor.id)
            yield row_num, "vendor", m.vendor.name
            yield row_num, "name", m.name
            for iface, a in q_attrs:
                yield row_num, f"{iface}_{a.name}", cls.clean_value(a, m.get_data(iface, a.name))
            ru = m.get_data("rackmount", "units")
            yield row_num, "ru", f"{ru}U" if ru else ""
