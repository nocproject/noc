# ----------------------------------------------------------------------
# objectds datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
# Python modules
from collections.abc import AsyncIterable, Iterable
from typing import Any

# NOC modules
from noc.inv.models.object import Object

from .base import BaseDataSource, FieldInfo


class ObjectDS(BaseDataSource):
    name = "objectds"

    fields = [
        FieldInfo(name="name"),
        FieldInfo(name="model"),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Iterable[str] | None = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[tuple[int, str, Any]]:
        data = Object.objects.all().scalar("name", "model")
        row_num = 0
        for name, model in data:
            row_num += 1
            yield row_num, "name", name
            yield row_num, "model", model.name
