# ----------------------------------------------------------------------
# cfgmetricscollector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.pm.models.metrictype import MetricType


class CfgMetricsCollectorDataStream(DataStream):
    name = "cfgmetrics"

    @classmethod
    def get_object(cls, id: str) -> Dict[str, Any]:
        mt = MetricType.objects.filter(id=id).first()
        if not mt or not mt.agent_mappings:
            raise KeyError()
        return {
            "id": str(mt.id),
            "table": mt.scope.table_name,
            "field": mt.field_name,
            "rules": [
                {"collector": m.collector, "field": m.field, "labels": [], "preference": n}
                for n, m in enumerate(mt.agent_mappings)
            ],
        }
