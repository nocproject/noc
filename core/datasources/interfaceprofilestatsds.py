# ----------------------------------------------------------------------
# Interface Profile Stats Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# Third-party modules
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource


class InterfaceProfileStatsDS(BaseDataSource):
    name = "interfaceprofilestatsds"

    fields = [
        FieldInfo(name="pool"),
        FieldInfo(name="profile"),
        FieldInfo(name="count", type=FieldType.UINT),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
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
