# ----------------------------------------------------------------------
# Interface Profile Stats Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
# Python modules
from collections.abc import AsyncIterable, Iterable

# NOC modules
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile

from .base import BaseDataSource, FieldInfo, FieldType


class InterfaceProfileStatsDS(BaseDataSource):
    name = "interfaceprofilestatsds"

    fields = [
        FieldInfo(name="pool"),
        FieldInfo(name="profile"),
        FieldInfo(name="count", type=FieldType.UINT),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Iterable[str] | None = None, *args, **kwargs
    ) -> AsyncIterable[tuple[str, str]]:
        d_count = Interface.objects.count()
        num = 0
        for num, p in enumerate(InterfaceProfile.objects.all()):
            n = Interface.objects.filter(profile=p).count()
            yield num, "pool", "-"
            yield num, "profile", p.name
            yield num, "count", n
            d_count -= n
        num += 1
        yield num, "pool", "-"
        yield num, "profile", "-"
        yield num, "count", d_count
