# ----------------------------------------------------------------------
# partnumbersds datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Any, Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.inv.models.objectmodel import ObjectModel


#     columns=["0", "1", "2", "3", "0", "1", "2", "3", "Name", "Description"],
#     title = _("Part Numbers")
class PartNumbersDS(BaseDataSource):
    name = "partnumbersds"

    fields = [
        FieldInfo(name="vendor"),
        FieldInfo(name="part_no0"),
        FieldInfo(name="part_no1"),
        FieldInfo(name="part_no2"),
        FieldInfo(name="part_no3"),
        FieldInfo(name="asset_part_no0"),
        FieldInfo(name="asset_part_no1"),
        FieldInfo(name="asset_part_no2"),
        FieldInfo(name="asset_part_no3"),
        FieldInfo(name="name"),
        FieldInfo(name="description"),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Any]]:
        row_num = 0
        for m in ObjectModel.objects.all():
            row_num += 1
            yield row_num, "vendor", m.vendor.name
            yield row_num, "part_no0", m.get_data("asset", "part_no0")
            yield row_num, "part_no1", m.get_data("asset", "part_no1")
            yield row_num, "part_no2", m.get_data("asset", "part_no2")
            yield row_num, "part_no3", m.get_data("asset", "part_no3")
            yield row_num, "asset_part_no0", m.get_data("asset", "asset_part_no0")
            yield row_num, "asset_part_no1", m.get_data("asset", "asset_part_no1")
            yield row_num, "asset_part_no2", m.get_data("asset", "asset_part_no2")
            yield row_num, "asset_part_no3", m.get_data("asset", "asset_part_no3")
            yield row_num, "name", m.name
            yield row_num, "description", m.description
