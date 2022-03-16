# ----------------------------------------------------------------------
# cfgmomapping datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.pool import Pool
from noc.main.models.label import Label


class CfgMOMappingDataStream(DataStream):
    name = "cfgmomapping"

    @classmethod
    def get_object(cls, id: str) -> Dict[str, Any]:
        mo = ManagedObject.objects.filter(id=id).values_list(
            "id",
            "bi_id",
            "is_managed",
            "pool",
            "fm_pool",
            "labels",
        )[:1]
        if not mo:
            raise KeyError()
        (
            mo_id,
            bi_id,
            is_managed,
            pool,
            fm_pool,
            labels,
        ) = mo[0]
        if not is_managed:
            raise KeyError()
        pool = fm_pool or pool
        return {
            "id": mo_id,
            "bi_id": bi_id,
            "pool": str(Pool.get_by_id(pool).name),
            "labels": labels,
            "metric_labels": list(
                Label.objects.filter(name__in=labels, expose_metric=True).values_list("name")
            ),
        }
