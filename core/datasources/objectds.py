# ----------------------------------------------------------------------
# objectds datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Any, Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.inv.models.object import Object


class ObjectDS(BaseDataSource):
    name = "objectds"

    fields = [
        FieldInfo(name="name"),
        FieldInfo(name="model"),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Any]]:
        data = Object.objects.all().scalar("name", "model")
        row_num = 0
        for name, model in data:
            row_num += 1
            yield row_num, "name", name
            yield row_num, "model", model.name
