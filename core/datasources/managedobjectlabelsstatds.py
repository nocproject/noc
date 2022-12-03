# ----------------------------------------------------------------------
# Managed Object Labels Stat Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, Any, AsyncIterable

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
    row_index = "managed_object_id"

    fields = [
        FieldInfo(name="managed_object_id", type="int64"),
    ] + [FieldInfo(name=f, type="bool") for f in get_labels()]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, Any]]:
        query_fields = [ff.name for ff in cls.fields[1:]]
        for mo_id, labels in ManagedObject.objects.filter().values_list("id", "labels").iterator():
            labels = set(labels)
            for ff in query_fields:
                yield ff, ff in labels
            yield "managed_object_id", mo_id
