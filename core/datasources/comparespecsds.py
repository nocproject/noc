# ----------------------------------------------------------------------
# Compare Specs Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.inv.models.objectmodel import ObjectModel


class CompareSpecsDS(BaseDataSource):
    name = "comparespecsds"

    fields = [
        FieldInfo(name="vendor_id"),
        FieldInfo(name="vendor"),
        FieldInfo(name="model"),
        FieldInfo(name="width"),
        FieldInfo(name="height"),
        FieldInfo(name="depth"),
        FieldInfo(name="ru"),
        FieldInfo(name="weight"),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        row_num = 0
        for m in ObjectModel.objects.filter(
            # old style (for version 23)
            # data__management__managed=True
            data__match={"interface": "management", "attr": "managed", "value": True}
        ):
            ru = m.get_data("rackmount", "units")
            ru = f"{ru}U" if ru else ""
            weight = m.get_data("weight", "weight")
            if weight:
                weight = str(weight)
                if m.get_data("weight", "is_recursive"):
                    weight += "+"
            else:
                weight = ""
            row_num += 1
            yield row_num, "vendor_id", str(m.vendor.id)
            yield row_num, "vendor", m.vendor.name
            yield row_num, "model", m.name
            yield row_num, "width", str(m.get_data("dimensions", "width") or "")
            yield row_num, "height", str(m.get_data("dimensions", "height") or "")
            yield row_num, "depth", str(m.get_data("dimensions", "depth") or "")
            yield row_num, "ru", ru
            yield row_num, "weight", weight
