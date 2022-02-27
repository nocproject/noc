# ----------------------------------------------------------------------
# Managed Object Labels Stat Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any

# Third-party modules
import pandas as pd

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.sa.models.managedobject import ManagedObject


def get_labels():
    labels = set()
    for s in (
        ManagedObject.objects.filter()
        .exclude(labels=None)
        .values_list("labels", flat=True)
        .distinct()
    ):
        labels.update(set(s))
    return sorted([t for t in labels if "{" not in t])


class ManagedObjectLabelsStatDS(BaseDataSource):
    name = "managedobjectlabelsstatds"

    fields = [
        FieldInfo(name="managed_object_id", type="int64"),
    ] + [FieldInfo(name=f, type="bool") for f in get_labels()]

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields, require_index=True)]
        return pd.DataFrame.from_records(
            data, index="managed_object_id", columns=[ff.name for ff in cls.fields]
        )

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        query_fields = [ff.name for ff in cls.fields[1:]]
        for mo_id, labels in ManagedObject.objects.filter().values_list("id", "labels").iterator():
            labels = set(labels)
            r = {ff: ff in labels for ff in query_fields}
            r["managed_object_id"] = mo_id
            yield r
